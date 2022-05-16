import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';
import { ApiService } from 'src/app/services/api/api.service';


@Component({
  selector: 'app-admin-users',
  templateUrl: './admin-users.component.html',
  styleUrls: ['./admin-users.component.scss']
})
export class AdminUsersComponent implements OnInit {
  userRoles: string[] = ['Surgeon', 'PMNR', 'Nurse', 'Office', 'Other'];
  editUser: boolean = false;
  index_complete: boolean = false;
  index_error = '';
  users: any[] = [];
  userUuid: string;

  addUserForm: FormGroup;
  userModalLoading: boolean = false;
  userModalError: boolean = false;
  userModalSuccess: boolean = false;

  userDeleteLoading: boolean = false;
  userDeleteError: boolean = false;
  userDeleteSuccess: boolean = false;

  constructor(
    private modalService: NgbModal, private _api: ApiService, private _formbuilder: FormBuilder) { }

  ngOnInit(): void {
    this.getUsers();
    this.createUserForm();
  }

  async delay(ms: number){
    await new Promise(resolve => setTimeout(resolve, ms));
  }

  getUsers() {
    this._api.globalGetRequest('users').subscribe((response: any) => {
      this.users = response;
    }, (error: any) => {
      console.log(error);
    });
  }

  createUserForm(){
    this.addUserForm = this._formbuilder.group({
      first_name: ['', [Validators.required]],
      last_name: ['',[Validators.required]],
      username: ['', [Validators.required]],
      password: ['', [Validators.required]],
      role: [''],
    });
  }

  openAddUserDialog(content, editUser: boolean = false, user: any = null) {
    if (editUser) {
      this.editUser = true;
      this.editUserAction(user);
      this.userUuid = user.uuid;
    } else {
      this.editUser = false;
    }
    this.modalService.open(content, { ariaLabelledBy: 'modal-basic-title' }).result.then(
      (result) => {
      
    }, (reason) => {
        
    });
  }

  createUser() {
    this.userModalLoading = true;
    const reqData = this.addUserForm.value;
    this._api.globalPostRequest('users', reqData).subscribe((response: any) => {
      this.userModalLoading = false;
      this.userModalSuccess = true;
      this.ngOnInit();
    }, (error: any) => {
      console.log(error);
      this.userModalLoading = false;
      this.userModalError = true;
    });
  }

  closeAddUserModal(){
    this.modalService.dismissAll();
    this.addUserForm.reset();
    this.userModalError = false;
    this.userModalLoading = false;
    this.userModalSuccess = false;
  }
  deleteUserAction(content, userUuid: string){
    this.modalService.open(content, {
      ariaLabelledBy: 'modal-basic-title'
    }).result.then((result) => {}, (reason) => {});
    this.userUuid = userUuid
  }

  closeDelModal(){
    this.userUuid = null;
    this.modalService.dismissAll();
    this.userDeleteError = false;
    this.userDeleteLoading = false;
    this.userDeleteSuccess = false;
  }

  deleteUser(){
    this.userDeleteLoading = true;
    this._api.globalDeleteRequest(`users/${this.userUuid}`).subscribe(
      (response: any) => {
      this.userDeleteLoading = false;
      this.userDeleteSuccess = true;
      this.ngOnInit();
    }, (error: any) => {
      this.userDeleteLoading = false;
      this.userDeleteError = true;
    });
  }

  editUserAction(user) {
    this.addUserForm = this._formbuilder.group({
      first_name: [user.first_name, [Validators.required]],
      last_name: [user.last_name, [Validators.required]],
      username: [user.username, [Validators.required, Validators.email]],
      password: [{value: user.password, disabled: true}, [Validators.required]],
      role: [user.role]
    });
  }

  editUserFun() {
    this.userModalLoading = true;
    const reqData = {
      first_name: this.addUserForm.value['first_name'],
      last_name: this.addUserForm.value['last_name'],
      username: this.addUserForm.value['username'],
      role: this.addUserForm.value['role']
    };

    this._api.globalPatchRequest(`users/${this.userUuid}`, reqData).subscribe((response: any) => {
      this.userModalLoading = false;
      this.userModalSuccess = true;
      this.ngOnInit();
    }, (error: any) => {
      this.userModalLoading = false;
      this.userModalError = true;
    });
  }
}
