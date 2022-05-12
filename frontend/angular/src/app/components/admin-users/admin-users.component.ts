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

  addUserForm: FormGroup;
  userModalLoading: boolean = false;
  userModalError: boolean = false;
  userModalSuccess: boolean = false;


  constructor(
    private modalService: NgbModal, private _api: ApiService, private _formbuilder: FormBuilder) { }

  ngOnInit(): void {
    this.getUsers();
    this.createUserForm();
  }

  async delay(ms: number){
    await new Promise(resolve => setTimeout(resolve, ms));
  }

  getUsers(){
    this._api.globalGetRequest('users').subscribe((response: any) =>{
      this.users = response;
      console.log(this.users);
    }, (error: any) => {
      console.log(error);
    })
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

  openAddUserDialog(content, editUser: boolean = false){
    if (editUser){
      this.editUser = true;
    }
    else{
      this.editUser = false;
    }
    this.modalService.open(content, {
      ariaLabelledBy: 'modal-basic_title'
    }).result.then((result) => {},
    (reason) => {});
  }

  createUser(){
    this.userModalLoading = true;
    const reqData = this.addUserForm.value;

    this._api.globalPostRequest('users', reqData).subscribe((response: any) => {
      this.userModalLoading = false;
      this.userModalSuccess = true;
      this.delay(3000);
      this.modalService.dismissAll();
      this.ngOnInit();
    }, (error: any) => {
      console.log(error);
      this.userModalLoading = false;
      this.userModalError = true;
    })
  }

  closeAddUserModal(){
    this.modalService.dismissAll();
  }
  deleteUserAction(content){
    this.modalService.open(content, {
      ariaLabelledBy: 'modal-basic-title'
    }).result.then((result) => {}, (reason) => {});
  }

  closeDelModal(){
    this.modalService.dismissAll();
  }

  deleteUserModal(){

  }
}
