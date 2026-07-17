import {
  ComponentFixture,
  TestBed,
} from '@angular/core/testing';
import { By } from '@angular/platform-browser';
import {
  provideRouter,
  RouterOutlet,
} from '@angular/router';
import {
  beforeEach,
  describe,
  expect,
  it,
} from 'vitest';

import { App } from './app';

describe('App', () => {
  let fixture: ComponentFixture<App>;

  beforeEach(async () => {
    await TestBed
      .configureTestingModule({
        imports: [
          App,
        ],
        providers: [
          provideRouter([]),
        ],
      })
      .compileComponents();

    fixture =
      TestBed.createComponent(App);

    fixture.detectChanges();
  });

  it('should create the app', () => {
    expect(
      fixture.componentInstance,
    ).toBeTruthy();
  });

  it(
    'should render the router outlet',
    () => {
      const routerOutlet =
        fixture.debugElement.query(
          By.directive(RouterOutlet),
        );

      expect(
        routerOutlet,
      ).not.toBeNull();
    },
  );
});