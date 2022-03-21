import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { NgPipesModule } from 'ngx-pipes';

import { RiskFaktorDropdownComponent } from './components/risk-faktor-dropdown/risk-faktor-dropdown.component';
import { SpineRiskScoreBarComponent } from './components/spine-risk-score-bar/spine-risk-score-bar.component';
import { SummaryTabComponent } from './components/summary-tab/summary-tab.component';
import { RouterModule } from '@angular/router';
import { SpineReportComponent } from './spine-report.component';
import { ImageViewerComponent } from './components/image-viewer/image-viewer.component';
import { FormsModule } from '@angular/forms';
import { ShareDialogComponent } from './components/share-dialog/share-dialog.component';
import { DownloadMenuComponent } from './components/download-menu/download-menu.component';
import { DetailTabComponent } from './components/detail-tab/detail-tab.component';
import { DetailBarsComponent } from './components/detail-bars/detail-bars.component';
import { MatCheckboxModule } from '@angular/material/checkbox';



@NgModule({
    declarations: [
        SpineReportComponent,
        RiskFaktorDropdownComponent,
        SpineRiskScoreBarComponent,
        SummaryTabComponent,
        ImageViewerComponent,
        ShareDialogComponent,
        DownloadMenuComponent,
        DetailTabComponent,
        DetailBarsComponent,
    ],
    imports: [
        CommonModule,
        FormsModule,
        MatCheckboxModule,
        NgPipesModule,
        RouterModule.forChild([
            { path: '', component: SpineReportComponent }
        ])
    ],
})
export class SpineReportModule { }
