import { Injectable, UnauthorizedException, OnModuleInit } from '@nestjs/common';
import { JwtService } from '@nestjs/jwt';
import { PrismaService } from '../prisma';
import * as bcrypt from 'bcrypt';
import { ConfigService } from '@nestjs/config';

@Injectable()
export class AuthService implements OnModuleInit {
  constructor(
    private prisma: PrismaService,
    private jwtService: JwtService,
    private configService: ConfigService,
  ) {}

  async onModuleInit() {
    // Auto create admin account if not exists
    const adminUsername = this.configService.get('ADMIN_USERNAME') || 'admin';
    const adminPassword = this.configService.get('ADMIN_PASSWORD') || 'MutsumiSaki2024!';

    const existingAdmin = await this.prisma.admin.findUnique({
      where: { username: adminUsername },
    });

    if (!existingAdmin) {
      const hashedPassword = await bcrypt.hash(adminPassword, 10);
      await this.prisma.admin.create({
        data: {
          username: adminUsername,
          password: hashedPassword,
        },
      });
      console.log(`Admin account created: ${adminUsername} / ${adminPassword}`);
    }
  }

  async validateAdmin(username: string, password: string) {
    const admin = await this.prisma.admin.findUnique({
      where: { username },
    });

    if (!admin) {
      throw new UnauthorizedException('Invalid credentials');
    }

    const isPasswordValid = await bcrypt.compare(password, admin.password);
    if (!isPasswordValid) {
      throw new UnauthorizedException('Invalid credentials');
    }

    return admin;
  }

  async login(username: string, password: string) {
    const admin = await this.validateAdmin(username, password);
    const payload = { sub: admin.id, username: admin.username };
    return {
      access_token: this.jwtService.sign(payload),
      admin: {
        id: admin.id,
        username: admin.username,
      },
    };
  }

  async validateToken(payload: any) {
    const admin = await this.prisma.admin.findUnique({
      where: { id: payload.sub },
    });
    return admin;
  }
}
