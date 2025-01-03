// system-spec.component.ts
import { Component, OnInit, ViewChild, ElementRef } from '@angular/core';
import { FormsModule } from '@angular/forms';
import * as ace from 'ace-builds';
import 'ace-builds/src-noconflict/mode-text';
import 'ace-builds/src-noconflict/theme-tomorrow_night';
import 'ace-builds/src-noconflict/ext-language_tools';
import { BackendService } from '../../backend.service';
import { HttpClient } from '@angular/common/http';
import { CommonModule } from '@angular/common';
import { DomSanitizer, SafeUrl } from '@angular/platform-browser';

@Component({
  selector: 'app-system-spec',
  standalone: true,
  templateUrl: './system-spec.component.html',
  styleUrls: ['./system-spec.component.css'],
  imports: [FormsModule, CommonModule]
})
export class SystemSpecComponent implements OnInit {
  @ViewChild('editor') private editor!: ElementRef<HTMLElement>;
  private aceEditor: any;
  fileContent: string = '';
  editorMode: string = 'text';
  compiledImageUrl: string = '';
  compiledImageSafeUrl: SafeUrl = '';

  constructor(private backendService: BackendService, private http: HttpClient, private sanitizer: DomSanitizer) {}

  ngOnInit() {
    // Initial content
    this.fileContent = `// Enter your UML or LTL code here
// The editor will automatically detect the language
// Example UML:
@startuml
class Example {
  +attribute: String
  +method()
}
@enduml
// Example LTL:
ltl property {
  []<>(state -> X response)
}`;
  }

  ngAfterViewInit() {
    // Initialize ace editor
    //ace.config.set('fontSize', '14px');
    ace.config.set('basePath', 'https://unpkg.com/ace-builds@latest/src-noconflict/');
    
    this.aceEditor = ace.edit(this.editor.nativeElement);
    this.aceEditor.session.setValue(this.fileContent);
    
    // Configure editor
    this.aceEditor.setTheme('ace/theme/tomorrow_night');
    this.aceEditor.session.setMode('ace/mode/text');
    this.aceEditor.setOptions({
      enableBasicAutocompletion: true,
      enableLiveAutocompletion: true,
      enableSnippets: true,
      showPrintMargin: false,
      tabSize: 2,
      wrap: true,
      minLines: 20,
      maxLines: 40,
      showGutter: true
    });

    // Listen for changes
    this.aceEditor.on('change', () => {
      this.fileContent = this.aceEditor.getValue();
      this.onCodeChange();
    });
  }

  onCodeChange(): void {
    const content = this.fileContent;
    if (this.fileContent.includes("uml:Model")) {
      this.editorMode = 'uml';
    }
    else if (content.includes('ltl')) {
      this.editorMode = 'ltl';
      this.aceEditor.session.setMode('ace/mode/text'); // Since LTL mode isn't built-in
    } else if (content.includes('@startuml')) {
      this.editorMode = 'uml';
      this.aceEditor.session.setMode('ace/mode/text'); // Since UML mode isn't built-in
    } else {
      this.editorMode = 'text';
      this.aceEditor.session.setMode('ace/mode/text');
    }
  }

  submitFile(): void {
    console.log('Submitted content:', this.fileContent);
  }

  ngOnDestroy() {
    if (this.aceEditor) {
      this.aceEditor.destroy();
    }
  }

  compileContent(): void {
    if (this.editorMode === 'uml') {
      this.compileUMLAndGeneratePNG();
    } else if (this.editorMode === 'ltl') {
      this.compileLTLAndGeneratePNG();
    }
  }

  compileUMLAndGeneratePNG(): void {
    console.log(this.fileContent);
    this.http.get<any>(`${this.backendService.apiUrl}/service/uml-to-png`, { params: { "umlContent": this.fileContent } })
      .subscribe(response => {
        this.compiledImageUrl = response.imageUrl;
        const timestamp = new Date().getTime(); // Current timestamp
        this.compiledImageSafeUrl = this.sanitizer.bypassSecurityTrustUrl(`${response.imageUrl}?t=${timestamp}`);
        console.log(this.compiledImageSafeUrl);
      });
  }

  compileLTLAndGeneratePNG(): void {
    this.http.get<any>(`${this.backendService.apiUrl}/service/xml-to-png`, { params: { "ltlContent": this.fileContent } })
      .subscribe(response => {
        this.compiledImageUrl = response.imageUrl;
      });
  }
}