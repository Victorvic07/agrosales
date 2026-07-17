import { UserRole } from '../../core/models/user-role';

export interface NavigationItem {
  label: string;
  icon: string;
  route: string;
  roles: UserRole[];
}