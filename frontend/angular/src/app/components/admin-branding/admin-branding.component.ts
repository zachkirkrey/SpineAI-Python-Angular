import { Component, OnInit } from '@angular/core';
import { UploadService } from 'src/app/services/upload/upload.service';

@Component({
    selector: 'app-admin-branding',
    templateUrl: './admin-branding.component.html',
    styleUrls: ['./admin-branding.component.scss']
})
export class AdminBrandingComponent implements OnInit {
    upload_image: any = ''
    showImgErr: any = ''
    constructor(private uploadService: UploadService) { }

    ngOnInit(): void { }
    onChange(event) {
        this.showImgErr = ''
        let reader = new FileReader();
        let file = event.target.files[0];
        const img = new Image();
        img.src = window.URL.createObjectURL(file);
        reader.readAsDataURL(file);
        reader.onload = () => {
            const width = img.naturalWidth
            const height = img.naturalHeight;
            window.URL.revokeObjectURL(img.src);
            if (event.target.files[0] && event.target.files[0].type !== 'image/png') {
                this.showImgErr = 'Please upload a file with type png only.'
                event.target.value = ''
            }
            else if (width !== 530 && height !== 30) {
                this.showImgErr = "Image should be 530 x 30 size"
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
        }
    }
    restoreImage() {
        localStorage.setItem('default-image', 'true')
        this.uploadService.setSpineLogo('true')
    }
}
