import { Component, inject } from '@angular/core';
import { MatIconModule } from '@angular/material/icon';
import { ActivatedRoute } from '@angular/router';

interface PageContent {
  description: string;
  icon: string;
}

@Component({
  selector: 'app-feature-placeholder',
  standalone: true,
  imports: [
    MatIconModule,
  ],
  templateUrl:
    './feature-placeholder.component.html',
  styleUrl:
    './feature-placeholder.component.scss',
})
export class FeaturePlaceholderComponent {
  private readonly route =
    inject(ActivatedRoute);

  private readonly content:
    Record<string, PageContent> = {
      Dashboard: {
        description:
          'Visão geral do AgroSales.',
        icon: 'dashboard',
      },
      Produtos: {
        description:
          'Cadastro e consulta de produtos.',
        icon: 'inventory_2',
      },
      Variações: {
        description:
          'Variações comerciais dos produtos.',
        icon: 'category',
      },
      Lotes: {
        description:
          'Controle de lotes e validade.',
        icon: 'warehouse',
      },
      Clientes: {
        description:
          'Cadastro e consulta de clientes.',
        icon: 'groups',
      },
      Pedidos: {
        description:
          'Fluxo comercial de pedidos.',
        icon: 'receipt_long',
      },
      Usuários: {
        description:
          'Gestão de usuários e perfis.',
        icon: 'manage_accounts',
      },
    };

  readonly title =
    this.route.snapshot.title ??
    'AgroSales';

  readonly description =
    this.content[this.title]
      ?.description ??
    'Módulo do AgroSales.';

  readonly icon =
    this.content[this.title]
      ?.icon ??
    'apps';
}