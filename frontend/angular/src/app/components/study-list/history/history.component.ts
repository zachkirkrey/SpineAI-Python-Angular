import {Component, Input, OnInit} from '@angular/core';
import {NgbActiveModal} from '@ng-bootstrap/ng-bootstrap';
import {Action, ApiService} from '../../../services/api/api.service';
import {shareReplay, tap} from 'rxjs/operators';
import {ActionListValues} from '../../../helpers/action-list.enum';

@Component({
  selector: 'app-history',
  templateUrl: './history.component.html',
  styleUrls: ['./history.component.scss']
})
export class HistoryComponent implements OnInit {

  @Input()
  studyId = '';

  actions: Action[] = [];
  actionList = ActionListValues;
  selectedAction = '';
  processing = false;
  updated = false;

  constructor(private activeModal: NgbActiveModal, private api: ApiService) { }

  ngOnInit(): void {
    this.reload();
  }

  private reload() {
    if (this.studyId) {
      this.api.getStudyActions(this.studyId)
        .pipe(shareReplay())
        .subscribe(
          actions => this.actions = actions
        );
    }
  }

  public dismiss() {
    this.activeModal.dismiss(this.updated);
  }

  submit() {
    this.processing = true;
    this.api.addStudyAction(this.studyId, {
      name: this.selectedAction,
    }).pipe(
      shareReplay(),
      tap(() => this.processing = false)
    ).subscribe(
      action => {
        this.actions.push(action);
        this.selectedAction = '';
        this.updated = true;
        this.dismiss();
      }
    );
  }
}
