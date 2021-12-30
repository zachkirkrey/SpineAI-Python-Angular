import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';

import { Observable, throwError } from 'rxjs';
import { catchError, retry } from 'rxjs/operators';

import { environment } from './../../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class UserService {

  private localStorage = window.localStorage;
  private oauthUrl = environment.oauth_url;
  private enabledUrl = this.oauthUrl + '/oauth2/enabled';
  private userUrl = this.oauthUrl + '/oauth2/user';
  private isEnabled = null;

  constructor(private http: HttpClient) {

  }

  public async isAuthEnabled() {
    if (this.isEnabled !== null) return await this.isEnabled;

    this.isEnabled = await this.http.get(this.enabledUrl).toPromise();
    return this.isEnabled;
  }

  public getUser() {
    if (environment.oauth_test) {
      return new Promise((resolve, reject) => {
        resolve({
          "applicationId":"0d196117-868e-49d5-86b0-90f8cc72f757",
          "email":"billy@spineai.com",
          "email_verified":true,
          "family_name":"Cao",
          "given_name":"Billy",
          "roles":[],
          "sub":"8552ada9-aee5-40cc-915f-f9519e9ec93c"
        });
      });
    }
    return this.http.get(this.userUrl).toPromise();
  }
}
