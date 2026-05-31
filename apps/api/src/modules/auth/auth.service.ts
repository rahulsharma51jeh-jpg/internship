import {
  BadRequestException,
  ConflictException,
  Injectable,
  UnauthorizedException,
} from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import { JwtService } from '@nestjs/jwt';
import { AccountStatus, Prisma, UserRole } from '@prisma/client';
import * as argon2 from 'argon2';
import { createHash, randomUUID } from 'crypto';
import { PrismaService } from '../../prisma/prisma.service';
import { LoginDto, RegisterDto } from './dto/auth.dto';
import { JwtPayload } from './strategies/jwt.strategy';

@Injectable()
export class AuthService {
  constructor(
    private readonly prisma: PrismaService,
    private readonly jwt: JwtService,
    private readonly config: ConfigService,
  ) {}

  async register(dto: RegisterDto) {
    const role = dto.role ?? UserRole.STUDENT;

    // Privileged roles can never be self-assigned through public registration.
    if (role === UserRole.ADMIN || role === UserRole.SUPER_ADMIN) {
      throw new BadRequestException('This role cannot be self-assigned');
    }
    if (role === UserRole.ORGANIZATION && !dto.companyName) {
      throw new BadRequestException('companyName is required for organization accounts');
    }

    const existing = await this.prisma.user.findUnique({ where: { email: dto.email } });
    if (existing) {
      throw new ConflictException('An account with this email already exists');
    }

    const passwordHash = await argon2.hash(dto.password);

    const data: Prisma.UserCreateInput = {
      email: dto.email,
      passwordHash,
      fullName: dto.fullName,
      roles: [role],
      status: AccountStatus.ACTIVE, // demo: auto-activate. Production: PENDING_VERIFICATION + email flow.
    };

    if (role === UserRole.STUDENT) {
      data.studentProfile = { create: {} };
    } else if (role === UserRole.ORGANIZATION) {
      data.organizationProfile = { create: { companyName: dto.companyName! } };
    }

    const user = await this.prisma.user.create({
      data,
      include: { studentProfile: true, organizationProfile: true },
    });

    return this.issueTokens(user.id, user.email, user.roles);
  }

  async login(dto: LoginDto) {
    const user = await this.prisma.user.findUnique({ where: { email: dto.email } });
    if (!user || !user.passwordHash) {
      throw new UnauthorizedException('Invalid credentials');
    }

    const valid = await argon2.verify(user.passwordHash, dto.password);
    if (!valid) {
      throw new UnauthorizedException('Invalid credentials');
    }
    if (user.status === AccountStatus.SUSPENDED || user.status === AccountStatus.BANNED) {
      throw new UnauthorizedException('Account is not active');
    }

    return this.issueTokens(user.id, user.email, user.roles);
  }

  async refresh(refreshToken: string) {
    let payload: JwtPayload;
    try {
      payload = await this.jwt.verifyAsync<JwtPayload>(refreshToken, {
        secret: this.config.get<string>('jwt.refreshSecret'),
      });
    } catch {
      throw new UnauthorizedException('Invalid refresh token');
    }

    const tokenHash = this.hashToken(refreshToken);
    const stored = await this.prisma.refreshToken.findFirst({
      where: { userId: payload.sub, tokenHash, revokedAt: null, expiresAt: { gt: new Date() } },
    });
    if (!stored) {
      throw new UnauthorizedException('Refresh token revoked or expired');
    }

    // Rotate: revoke the used token, issue a fresh pair.
    await this.prisma.refreshToken.update({ where: { id: stored.id }, data: { revokedAt: new Date() } });
    return this.issueTokens(payload.sub, payload.email, payload.roles as UserRole[]);
  }

  async logout(userId: string, refreshToken: string) {
    const tokenHash = this.hashToken(refreshToken);
    await this.prisma.refreshToken.updateMany({
      where: { userId, tokenHash, revokedAt: null },
      data: { revokedAt: new Date() },
    });
    return { success: true };
  }

  async me(userId: string) {
    const user = await this.prisma.user.findUnique({
      where: { id: userId },
      include: { studentProfile: true, organizationProfile: true },
    });
    if (!user) {
      throw new UnauthorizedException();
    }
    const { passwordHash, ...safe } = user;
    void passwordHash;
    return safe;
  }

  // ── helpers ──────────────────────────────────────────────────────────────

  private async issueTokens(userId: string, email: string, roles: UserRole[]) {
    const payload: JwtPayload = { sub: userId, email, roles };

    const accessToken = await this.jwt.signAsync(payload, {
      secret: this.config.get<string>('jwt.accessSecret'),
      expiresIn: this.config.get<string>('jwt.accessTtl'),
    });

    const refreshToken = await this.jwt.signAsync({ ...payload, jti: randomUUID() }, {
      secret: this.config.get<string>('jwt.refreshSecret'),
      expiresIn: this.config.get<string>('jwt.refreshTtl'),
    });

    // Persist a hash of the refresh token so it can be revoked / rotated.
    await this.prisma.refreshToken.create({
      data: {
        userId,
        tokenHash: this.hashToken(refreshToken),
        expiresAt: this.computeExpiry(this.config.get<string>('jwt.refreshTtl') ?? '7d'),
      },
    });

    return {
      accessToken,
      refreshToken,
      tokenType: 'Bearer',
      user: { id: userId, email, roles },
    };
  }

  private hashToken(token: string): string {
    return createHash('sha256').update(token).digest('hex');
  }

  private computeExpiry(ttl: string): Date {
    const match = /^(\d+)([smhd])$/.exec(ttl);
    const now = Date.now();
    if (!match) return new Date(now + 7 * 24 * 60 * 60 * 1000);
    const value = parseInt(match[1], 10);
    const unitMs: Record<string, number> = { s: 1000, m: 60_000, h: 3_600_000, d: 86_400_000 };
    return new Date(now + value * unitMs[match[2]]);
  }
}
