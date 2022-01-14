import { NgModule } from '@angular/core';
import { HttpClientModule } from '@angular/common/http';
import { BrowserModule } from '@angular/platform-browser';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { FormsModule } from '@angular/forms';
import { ReactiveFormsModule } from '@angular/forms';
import { RouterModule, Router, Routes } from '@angular/router';
import { MatNativeDateModule } from '@angular/material/core';
import { MatDatepickerModule } from '@angular/material/datepicker';
import {MatButtonModule} from '@angular/material/button';
import {MatCheckboxModule} from '@angular/material/checkbox';
import {MatIconModule} from '@angular/material/icon';
import {NgbModule } from '@ng-bootstrap/ng-bootstrap';

import { NgPipesModule } from 'ngx-pipes';

import { AppComponent } from './app.component';
import {MatMenuModule} from '@angular/material/menu';

import { DebugInfoComponent } from './components/debug-info/debug-info.component';
import { LoginFormComponent } from './components/login-form/login-form.component';
import { IntakeFormComponent } from './components/intake-form/intake-form.component';
import { LegacyReportComponent, LegacyReportData, SafePipe } from './components/legacy-report/legacy-report.component';
import { StudyListComponent } from './components/study-list/study-list.component';


import * as $ from 'jquery';
import { FetchFormComponent } from './components/fetch-form/fetch-form.component';
import { IngestionListComponent } from './components/fetch-form/ingestion-list/ingestion-list.component';

const appRoutes: Routes = [
  { path: 'debug', component: DebugInfoComponent },
  { path: 'login', component: LoginFormComponent },
  { path: 'study_legacy/:study_id', component: LegacyReportComponent },
  { path: 'study/:study_id', loadChildren: () => import('./components/spine-report/spine-report.module').then(res => res.SpineReportModule) },
  { path: 'studies', component: StudyListComponent },
  { path: 'intake', component: IntakeFormComponent },
  { path: 'fetch', component: FetchFormComponent },
  { path: '**',
    redirectTo: '/studies',
    pathMatch: 'full'
  },
]

@NgModule({
  declarations: [
    AppComponent,
    DebugInfoComponent,
    FetchFormComponent,
    IngestionListComponent,
    IntakeFormComponent,
    LegacyReportComponent,
    LoginFormComponent,
    SafePipe,
    StudyListComponent,
  ],
  imports: [
    BrowserModule,
    BrowserAnimationsModule,
    FormsModule,
    MatButtonModule,
    HttpClientModule,
    MatDatepickerModule,
    MatCheckboxModule,
    MatIconModule,
    MatMenuModule,
    MatNativeDateModule,
    NgbModule,
    NgPipesModule,
    ReactiveFormsModule,
    RouterModule.forRoot(appRoutes, { relativeLinkResolution: 'legacy' })
  ],
  providers: [LegacyReportData],
  bootstrap: [AppComponent]
})
export class AppModule { }
