import { ValidationPipe, Logger } from '@nestjs/common';
import { NestFactory, Reflector } from '@nestjs/core';
import { DocumentBuilder, SwaggerModule } from '@nestjs/swagger';
import { AppModule } from './app.module';
import { AllExceptionsFilter } from './common/filters/all-exceptions.filter';
import { TransformInterceptor } from './common/interceptors/transform.interceptor';

async function bootstrap(): Promise<void> {
  const app = await NestFactory.create(AppModule, { bufferLogs: false });
  const logger = new Logger('Bootstrap');

  // Security & cross-origin
  app.setGlobalPrefix('api', { exclude: ['health'] });
  app.enableCors({
    origin: (process.env.WEB_URL ?? 'http://localhost:3000').split(','),
    credentials: true,
  });

  // Global validation: strip unknown props, transform payloads to DTO types
  app.useGlobalPipes(
    new ValidationPipe({
      whitelist: true,
      forbidNonWhitelisted: true,
      transform: true,
      transformOptions: { enableImplicitConversion: true },
    }),
  );

  // Consistent error + response envelopes
  app.useGlobalFilters(new AllExceptionsFilter());
  app.useGlobalInterceptors(new TransformInterceptor());

  // OpenAPI / Swagger
  const config = new DocumentBuilder()
    .setTitle('Infinity Interns API')
    .setDescription('REST API for the Infinity Interns platform')
    .setVersion('1.0')
    .addBearerAuth()
    .build();
  const document = SwaggerModule.createDocument(app, config);
  SwaggerModule.setup('docs', app, document);

  const port = parseInt(process.env.API_PORT ?? '4000', 10);
  await app.listen(port);
  logger.log(`🚀 API ready at http://localhost:${port}/api`);
  logger.log(`📚 Swagger docs at http://localhost:${port}/docs`);
}

void bootstrap();
