import { AsyncPipe } from '@angular/common';
import {
  BreakpointObserver,
} from '@angular/cdk/layout';
import {
  Component,
  inject,
  ViewChild,
} from '@angular/core';
import {
  MatSidenav,
  MatSidenavModule,
} from '@angular/material/sidenav';
import { RouterOutlet } from '@angular/router';
import { map } from 'rxjs';

import { SidebarComponent } from '../sidebar/sidebar.component';
import { TopbarComponent } from '../topbar/topbar.component';

@Component({
  selector: 'app-shell',
  standalone: true,
  imports: [
    AsyncPipe,
    MatSidenavModule,
    RouterOutlet,
    SidebarComponent,
    TopbarComponent,
  ],
  templateUrl:
    './app-shell.component.html',
  styleUrl:
    './app-shell.component.scss',
})
export class AppShellComponent {
  private readonly breakpoints =
    inject(BreakpointObserver);

  @ViewChild(MatSidenav)
  sidenav?: MatSidenav;

  readonly isMobile$ =
    this.breakpoints
      .observe('(max-width: 900px)')
      .pipe(
        map(
          (result) =>
            result.matches,
        ),
      );

  toggleMenu(): void {
    void this.sidenav?.toggle();
  }
}