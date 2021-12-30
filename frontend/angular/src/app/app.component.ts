import { Location } from '@angular/common';
import { Component } from '@angular/core';
import { Router, NavigationEnd } from '@angular/router';

import { environment } from './../environments/environment';
import { PageType, WhiteLabel } from './app.config';
import { LegacyReportData } from './components/legacy-report/legacy-report.component';

import { UserService } from './services/user/user.service';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: [
    './app.component.scss',
  ]
})
export class AppComponent {
  environment = environment;
  title = 'SpineAI Demo';
  pageType: PageType;
  studyId: string;

  loggedIn: boolean = false;
  user: any = null;

  constructor(
    private router: Router,
    private segResultsData: LegacyReportData,
    private userService: UserService,
    private location: Location
  ) {
    router.events.subscribe(event => {
      if (event instanceof NavigationEnd ) {
        if (event.urlAfterRedirects.includes('study')) {
          this.pageType = PageType.VIEW_REPORT;
        } else if (event.urlAfterRedirects.includes('studies')) {
          this.pageType = PageType.STUDIES;
        } else if (event.urlAfterRedirects.includes('login')) {
          this.pageType = PageType.LOGIN;
        } else if (event.urlAfterRedirects.includes('intake')) {
          this.pageType = PageType.INTAKE;
        } else if (event.urlAfterRedirects.includes('fetch')) {
          this.pageType = PageType.FETCH;
        }
      }
    });
  }

  onLoadReport() {
    this.router.navigate(['studies']);
  }

  onProcessData() {
    this.router.navigate(['intake']);
  }

  onDICOMFetch() {
    this.router.navigate(['fetch']);
  }

  onViewReport() {
    if (this.segResultsData.studyId != '') {
      this.studyId = this.segResultsData.studyId;
      this.router.navigate(['study' + '/' + this.segResultsData.studyId]);
    }
  }

  async ngOnInit() {
    for (var label of WhiteLabel) {
      if (window.location.host.search(label.url) >= 0) {
        $('#logo').attr('src', label.logoImg);
        for (var logoCss of label.logoCss) {
          $('#logo').css(logoCss[0], logoCss[1]);
        }
        if (label.showSubLogo) {
          $('#sublogo').show();
        }
      }
      // if (true) {
      //   $('#logo').attr('src', label.logoImg);
      //   for (var logoCss of label.logoCss) {
      //     $('#logo').css(logoCss[0], logoCss[1]);
      //   }
      //   if (label.showSubLogo) {
      //     $('#sublogo').show();
      //   }
      //   break;
      // }

    }
    if (await this.userService.isAuthEnabled()) {
      // TODO(billy): enforce types using json schema.
      try {
        let user: any = await this.userService.getUser();
        if (user.error) {
          this.router.navigate(['login']);
        } else {
          this.loggedIn = true;
          this.user = user;
          if (!environment.production) console.log('logged in');
          if (this.location.path().includes('login')) {
            this.router.navigate(['']);
          }
        }
      } catch(err) {
        console.error(err);
        this.router.navigate(['login']);
      }
    }
  }
}
