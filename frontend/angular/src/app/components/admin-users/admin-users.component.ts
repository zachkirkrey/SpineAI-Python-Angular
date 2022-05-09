import { Component, OnInit } from '@angular/core';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';


@Component({
  selector: 'app-admin-users',
  templateUrl: './admin-users.component.html',
  styleUrls: ['./admin-users.component.scss']
})
export class AdminUsersComponent implements OnInit {
  userRoles: string[] = ['Surgeon', 'PMNR', 'Nurse', 'Office', 'Other'];
  editUser: boolean = false;

  constructor(private modalService: NgbModal) { }

  ngOnInit(): void {
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
