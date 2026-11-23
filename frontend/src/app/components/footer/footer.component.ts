import { CommonModule } from '@angular/common';
import { Component, Input } from '@angular/core';
import { RouterModule } from '@angular/router';

@Component({
  selector: 'app-footer',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './footer.component.html',
  styleUrl: './footer.component.css'
})
export class FooterComponent {
  @Input() title: string = "[Logo o titulo]";
  @Input() appName: string = "[Titulo app]";

  currentYear: number = new Date().getFullYear();

  navLinks = [
    { label: 'Noticias', path: '#' },
    { label: 'Contactanos', path: '#' },
    { label: 'Tus favoritos', path: '#' },
    { label: 'Publica tu historia', path: '#' }
  ];
}
