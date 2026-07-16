import { TestBed } from '@angular/core/testing';

import { AuthStorageService } from './auth-storage.service';
import { StoredSession } from '../models/auth.models';
import { UserRole } from '../models/user-role';

describe('AuthStorageService', () => {
  let service: AuthStorageService;

  const session: StoredSession = {
    accessToken: 'token',
    user: {
      id: 'user-id',
      name: 'Usuário',
      email: 'user@agrosales.com',
      role: UserRole.VENDEDOR,
    },
  };

  beforeEach(() => {
    localStorage.clear();
    sessionStorage.clear();

    TestBed.configureTestingModule({});
    service = TestBed.inject(AuthStorageService);
  });

  it('stores remembered sessions in localStorage', () => {
    service.save(session, true);

    expect(localStorage.getItem('agrosales.session')).not.toBeNull();
    expect(sessionStorage.getItem('agrosales.session')).toBeNull();
  });

  it('stores temporary sessions in sessionStorage', () => {
    service.save(session, false);

    expect(sessionStorage.getItem('agrosales.session')).not.toBeNull();
    expect(localStorage.getItem('agrosales.session')).toBeNull();
  });

  it('clears both storages', () => {
    service.save(session, true);
    service.clear();

    expect(service.read()).toBeNull();
  });
});