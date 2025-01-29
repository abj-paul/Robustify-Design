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
import { forkJoin, Observable } from 'rxjs';
import { ConstantService } from '../../constant.service';

@Component({
  selector: 'app-spec-template',
  standalone: true,
  templateUrl: './spec-template.component.html',
  styleUrls: ['./spec-template.component.css'],
  imports: [FormsModule, CommonModule]
})
export class SpecTemplateComponent implements OnInit {
  @ViewChild('editor') private editor!: ElementRef<HTMLElement>;
  @ViewChild('fileInput') private fileInput!: ElementRef<HTMLInputElement>;
  private aceEditor: any;
  fileContent: string = '';
  editorMode: string = 'text';
  compiledImageUrl: string = '';
  compiledImageSafeUrl: SafeUrl = '';
  isSaved = false;
  isUploading = false; 
  invalidCodeFormat = false;
  compilationError = false;

  constructor(private backendService: BackendService, private http: HttpClient, private sanitizer: DomSanitizer, private constantService: ConstantService) {}

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
    this.fetchSystemSpec();
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
    this.invalidCodeFormat = true; // Assume invalid by default
    
    if (this.fileContent.includes("uml:Model")) {
      this.editorMode = 'uml';
      this.invalidCodeFormat = false;
    }
    else if (content.includes('= (')) {
      this.editorMode = 'ltl';
      this.invalidCodeFormat = false;
      this.aceEditor.session.setMode('ace/mode/text');
    } else if (content.includes('@startuml')) {
      this.editorMode = 'uml';
      this.invalidCodeFormat = false;
      this.aceEditor.session.setMode('ace/mode/text');
    } else {
      // Check if content is valid JSON
      try {
        JSON.parse(content);
        this.editorMode = 'text';
        this.invalidCodeFormat = false;
      } catch (e) {
        // If not JSON and not UML/LTL, mark as invalid
        this.editorMode = 'text';
        this.invalidCodeFormat = true;
      }
      this.aceEditor.session.setMode('ace/mode/text');
    }
  }

  compileUMLAndGeneratePNG(): void {
    this.compilationError = false; // Reset error state
    console.log(this.fileContent);
    this.http.get<any>(`${this.backendService.apiUrl}/service/uml-to-png`, { params: { "umlContent": this.fileContent } })
      .subscribe({
        next: (response) => {
          if (response.imageUrl) {
            this.compiledImageUrl = response.imageUrl;
            const timestamp = new Date().getTime();
            this.compiledImageSafeUrl = this.sanitizer.bypassSecurityTrustUrl(`${response.imageUrl}?t=${timestamp}`);
            console.log(this.compiledImageSafeUrl);
          } else {
            this.compilationError = true;
          }
        },
        error: (error) => {
          console.error('Compilation failed:', error);
          this.compilationError = true;
        }
      });
  }
  
  handleFileInput(event: Event): void {
    const input = event.target as HTMLInputElement;
    const files = input.files;
    
    if (!files || files.length === 0) return;

    this.isUploading = true;
    let combinedContent = '';
    const fileReadPromises: Promise<{ name: string, content: string }>[] = [];

    // Create array of promises for reading files
    Array.from(files).forEach(file => {
      const promise = new Promise<{ name: string, content: string }>((resolve) => {
        const reader = new FileReader();
        reader.onload = (e: ProgressEvent<FileReader>) => {
          const content = e.target?.result as string;
          resolve({ name: file.name, content });
        };
        reader.readAsText(file);
      });
      fileReadPromises.push(promise);
    });

    // Process all files
    Promise.all(fileReadPromises).then(async (fileResults) => {
      // Combine content for editor
      combinedContent = fileResults.map(f => f.content).join('\n\n');
      this.fileContent = combinedContent;
      this.aceEditor.session.setValue(this.fileContent);
      this.onCodeChange();

      // Save individual files and update spec
      await this.saveUploadedFiles(fileResults);
      this.isUploading = false;
    });
  }

  async saveUploadedFiles(fileResults: { name: string, content: string }[]): Promise<void> {
    const project = this.constantService.getProject();
    const projectFolder = `projects/${project.name}-${project.id}`;
    
    // Create an array of observables for file upload requests
    const uploadRequests = fileResults.map(fileResult => {
      const formData = new FormData();
      formData.append('filename', fileResult.name);
      formData.append('specification', fileResult.content); // Now using individual file content
      formData.append('project_folder', projectFolder);
      
      return this.http.post(
        `${this.backendService.secondApiUrl}/upload/specification/`,
        formData
      );
    });

    // Add the spec update request with combined content
    uploadRequests.push(
      this.updateSystemSpecService(
        project.id, 
        fileResults.map(f => f.content).join('\n\n')
      )
    );

    try {
      const results = await forkJoin(uploadRequests).toPromise();
      console.log('All files uploaded successfully:', results);
      
      this.isSaved = true;
      setTimeout(() => (this.isSaved = false), 4000);
    } catch (error) {
      console.error('Error uploading files:', error);
    }
  }

triggerFileInput(): void {
  this.fileInput.nativeElement.click();
}

updateSystemSpecService(projectId: number, content: string): Observable<any> {
  const url = `${this.backendService.apiUrl}/projects/${projectId}/${this.constantService.getActiveTab()}_spec`;
  
  const formData = new FormData();
  formData.append('content', content);

  return this.http.post(url, formData);
}

  updateSpec() {
    console.log(`For project ${this.constantService.getProject().id}, I am sending ${this.fileContent}`);

    this.updateSystemSpecService(this.constantService.getProject().id, this.fileContent)
      .subscribe(
        response => {
          this.isSaved = true;
          setTimeout(() => (this.isSaved = false), 4000); // Hide message after 2 seconds
          console.log('Update successful:', response);
        },
        error => {
          console.error('Update failed:', error);
        }
      );
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


  compileLTLAndGeneratePNG(): void {
    this.http.get<any>(`${this.backendService.apiUrl}/service/lts-to-png`, { params: { "ltlContent": this.fileContent } })
      .subscribe(response => {
        this.compiledImageUrl = response.imageUrl;
      });
  }
  fetchSystemSpec(): void {
    console.log("DEBUG: Loading content from db to sync dashboard.");
    const url = `${this.backendService.apiUrl}/projects/${this.constantService.getProject().id}/${this.constantService.getActiveTab()}_spec`;
  
    this.http.get<{ spec: any }>(url).subscribe({
      next: (response) => {
        console.log("DEBUG Response:", response);
  
        // Check if spec is a string
        if (typeof response.spec === 'string') {
          this.fileContent = response.spec;
          this.aceEditor?.session.setValue(this.fileContent); // Load into editor
        } else if (response.spec == null){
          console.log("Loaded null from frontend");
        }
        else {
          console.warn("DEBUG: Response is not a string. Converting to JSON format.");
          this.fileContent = JSON.stringify(response.spec, null, 2); // Pretty print JSON
          this.aceEditor?.session.setValue(this.fileContent);
        }
      },
      error: (err) => {
        console.error('Failed to fetch system specification:', err);
      }
    });
  }
  
  
}