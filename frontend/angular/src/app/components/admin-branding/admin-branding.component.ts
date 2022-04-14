import { Component, OnInit } from '@angular/core';
import { UploadService } from 'src/app/services/upload/upload.service';
import { Router } from '@angular/router';
import { environment } from 'src/environments/environment';
import { v4 as uuidv4 } from 'uuid';
import * as moment from 'moment';

@Component({
    selector: 'app-admin-branding',
    templateUrl: './admin-branding.component.html',
    styleUrls: ['./admin-branding.component.scss']
})
export class AdminBrandingComponent implements OnInit {
    upload_image: any = ''
    showImgErr: any = ''
    token: any
    base64_strng: any
    action_error: any
    constructor(private uploadService: UploadService, private router: Router) {
        this.token = localStorage.getItem('token')
    }

    ngOnInit(): void { }
    onChange(event) {
        this.showImgErr = ''
        let reader = new FileReader();
        let file = event.target.files[0];
        const img = new Image();
        img.src = window.URL.createObjectURL(file);
        reader.readAsDataURL(file);
        reader.onload = () => {
            this.base64_strng = reader.result
            const width = img.naturalWidth
            const height = img.naturalHeight;
            window.URL.revokeObjectURL(img.src);
            if (event.target.files[0] && event.target.files[0].type !== 'image/png') {
                this.showImgErr = 'Please upload a file with type png only.'
                event.target.value = ''
            }
            else if (width != 530 && height != 150) {
                this.showImgErr = "Image should be 530 x 150 size"
                event.target.value = ''
            }
            else {
                this.upload_image = event.target.files[0]
            }

        }
    }
    saveImage() {
        if (this.upload_image == '') {
            this.showImgErr = 'Please upload the image'
        } else {
            this.showImgErr = ''
            this.uploadService.setSpineLogo('false')
            localStorage.setItem('default-image', 'false')
            this.saveLogo()
        }
    }
    restoreImage() {
        localStorage.setItem('default-image', 'true')
        this.uploadService.setSpineLogo('true')
    }
    navigate() {
        this.router.navigate(['studies'])
    }
    saveLogo() {
        let formatted_time = moment(new Date()).format("YYYY-MM-DD HH:mm:ss");
        let logo_url = `${environment.api_url}/logoimage`
        let req_data = {
            'uuid': uuidv4(),
            'creation_datetime': formatted_time,
            'png_base64_str': this.base64_strng,
            'active': true
        }
        $.ajax({
            url: logo_url,
            dataType: 'json',
            type: "POST",
            headers: {
                "Authorization": 'Bearer ' + this.token
            },
            data: req_data,
        }).done(function (data) {
            if ('error' in data) { }
            else {
                localStorage.setItem('logo-img', data.png_base64_str)
                this.uploadService.setSpineImgLogo(data.png_base64_str)
            }
        }.bind(this)).fail(function (jqXHR, textStatus, errorThrown) {
            this.action_error = `Data Not ${logo_url}.`;
        }.bind(this)).always(() => {
        });
    }
}
