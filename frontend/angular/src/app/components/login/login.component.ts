import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { environment } from 'src/environments/environment';
import { v4 as uuidv4 } from 'uuid';

@Component({
    selector: 'app-login',
    templateUrl: './login.component.html',
    styleUrls: ['./login.component.sass']
})
export class LoginComponent implements OnInit {

    login: any
    password: any
    action_error: string;
    email_error: boolean = false
    readonly login_url = `${environment.api_url}/user`;
    constructor(private route: Router) {
        localStorage.removeItem("token")
    }

    ngOnInit(): void {
        localStorage.removeItem("token")
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
        let req_data = {
            "uuid": uuidv4(),
            "username": this.login,
            "password": this.password,
        }
        $.ajax({
            url: this.login_url,
            dataType: 'json',
            type: "POST",
            data: req_data,
        }).done(function (data) {
            if ('error' in data) {
                this.action_error = data['error'];
            } else {
                console.log('savelogin', data)
                localStorage.setItem('token', data.token)
                this.route.navigate(['/studies'])

            }
        }.bind(this)).fail(function (jqXHR, textStatus, errorThrown) {
            this.action_error = `Data Not ${this.login_url}.`;
        }.bind(this)).always(() => {
        });

    }
}
