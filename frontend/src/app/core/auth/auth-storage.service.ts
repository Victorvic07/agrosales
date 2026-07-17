import { Injectable } from '@angular/core';

import { StoredSession } from '../models/auth.models';

@Injectable({ providedIn: 'root' })
export class AuthStorageService {
  private readonly key = 'agrosales.session';

  save(session: StoredSession, remember: boolean): void {
    this.clear();

    const storage = remember ? localStorage : sessionStorage;
    storage.setItem(this.key, JSON.stringify(session));
  }

  read(): StoredSession | null {
    const raw =
      localStorage.getItem(this.key) ??
      sessionStorage.getItem(this.key);

    if (!raw) {
      return null;
    }

    try {
      return JSON.parse(raw) as StoredSession;
    } catch {
      this.clear();
      return null;
    }
  }

  clear(): void {
    localStorage.removeItem(this.key);
    sessionStorage.removeItem(this.key);
  }
}