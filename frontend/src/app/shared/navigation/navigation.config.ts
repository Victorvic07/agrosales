import { UserRole } from '../../core/models/user-role';
import { NavigationItem } from './navigation-item';

const allRoles: UserRole[] = [
  UserRole.ADMINISTRADOR,
  UserRole.PRODUTOR,
  UserRole.VENDEDOR,
];

export const NAVIGATION_ITEMS: NavigationItem[] = [
  {
    label: 'Dashboard',
    icon: 'dashboard',
    route: '/dashboard',
    roles: allRoles,
  },
  {
    label: 'Produtos',
    icon: 'inventory_2',
    route: '/products',
    roles: allRoles,
  },
  {
    label: 'Variações',
    icon: 'category',
    route: '/product-variations',
    roles: [
      UserRole.ADMINISTRADOR,
      UserRole.PRODUTOR,
    ],
  },
  {
    label: 'Lotes',
    icon: 'warehouse',
    route: '/lots',
    roles: [
      UserRole.ADMINISTRADOR,
      UserRole.PRODUTOR,
    ],
  },
  {
    label: 'Clientes',
    icon: 'groups',
    route: '/customers',
    roles: allRoles,
  },
  {
    label: 'Pedidos',
    icon: 'receipt_long',
    route: '/orders',
    roles: allRoles,
  },
  {
    label: 'Usuários',
    icon: 'manage_accounts',
    route: '/users',
    roles: [
      UserRole.ADMINISTRADOR,
    ],
  },
];