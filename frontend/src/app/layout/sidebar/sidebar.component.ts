import {
  Component,
  computed,
} from '@angular/core';
import { MatIconModule } from '@angular/material/icon';
import { MatListModule } from '@angular/material/list';
import {
  RouterLink,
  RouterLinkActive,
} from '@angular/router';

import { AuthService } from '../../core/auth/auth.service';
import { NAVIGATION_ITEMS } from '../../shared/navigation/navigation.config';

@Component({
  selector: 'app-sidebar',
  standalone: true,
  imports: [
    MatIconModule,
    MatListModule,
    RouterLink,
    RouterLinkActive,
  ],
  templateUrl: './sidebar.component.html',
  styleUrl: './sidebar.component.scss',
})
export class SidebarComponent {
  readonly items = computed(() => {
    const role =
      this.auth.currentUser()?.role;

    if (!role) {
      return [];
    }

    return NAVIGATION_ITEMS.filter(
      (item) => item.roles.includes(role),
    );
  });

  constructor(
    readonly auth: AuthService,
  ) {}
}