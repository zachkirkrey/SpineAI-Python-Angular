import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';

import { UserService } from '../../services/user/user.service';

import { environment } from './../../../environments/environment';

@Component({
  selector: 'app-login-form',
  templateUrl: './login-form.component.html',
  styleUrls: ['./login-form.component.sass']
})
export class LoginFormComponent implements OnInit {

  public environment = environment;

  constructor(
    private router: Router,
    private userService: UserService
  ) { }

  async ngOnInit() {
    if (!await this.userService.isAuthEnabled()) {
      this.router.navigate(['']);
    }
  }

}
