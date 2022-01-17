import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';

@Component({
    selector: 'app-login',
    templateUrl: './login.component.html',
    styleUrls: ['./login.component.sass']
})
export class LoginComponent implements OnInit {

    login: any
    password: any
    email_error: boolean = false
    constructor(private route: Router) { }

    ngOnInit(): void {
    }

    emailValidate(value) {
        let regex = new RegExp('[a-z0-9]+@[a-z]+\.[a-z]{2,3}');
        let email_validate = regex.test(value)
        if (email_validate == false) {
            this.email_error = true
        } else {
            this.email_error = false
        }
    }
    signIn() {
        console.log('SignIn', this.login, this.password)
        this.route.navigate(['/studies'])

    }

}
