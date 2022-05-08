import { Component, OnInit } from '@angular/core';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';


@Component({
  selector: 'app-admin-users',
  templateUrl: './admin-users.component.html',
  styleUrls: ['./admin-users.component.scss']
})
export class AdminUsersComponent implements OnInit {
  userRoles: string[] = ['Surgeon', 'PMNR', 'Nurse', 'Office', 'Other']

  constructor(private modelService: NgbModal) { }

  ngOnInit(): void {
  }

  openAddUserDialog(content){
    this.modelService.open(content, {
      ariaLabelledBy: 'modal-basic_title'
    }).result.then((result) => {},
    (reason) => {});
  }

  closeModal(){
    this.modelService.dismissAll();
  }
}
