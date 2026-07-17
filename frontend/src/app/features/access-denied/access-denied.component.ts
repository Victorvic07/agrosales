import { Component } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-access-denied',
  standalone: true,
  imports: [
    MatButtonModule,
    RouterLink,
  ],
  template: `
    <main class="status-page">
      <span>403</span>

      <h1>Acesso negado</h1>

      <p>
        Seu perfil não possui permissão
        para acessar esta página.
      </p>

      <a
        mat-flat-button
        routerLink="/dashboard"
      >
        Voltar ao Dashboard
      </a>
    </main>
  `,
  styles: [`
    .status-page {
      display: grid;
      min-height: 100dvh;
      place-content: center;
      justify-items: center;
      padding: 2rem;
      text-align: center;
      background: #f4f7f5;
    }

    span {
      color: #ef7d2d;
      font-size: 5rem;
      font-weight: 800;
    }

    h1 {
      margin-bottom: 0.5rem;
    }

    p {
      max-width: 420px;
      color: #68746c;
    }
  `],
})
export class AccessDeniedComponent {}