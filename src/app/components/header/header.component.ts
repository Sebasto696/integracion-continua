import { CommonModule } from '@angular/common';
import { Component, Input } from '@angular/core';
import { RouterModule } from '@angular/router';

@Component({
  selector: 'app-header',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './header.component.html',
  styleUrl: './header.component.css'
})
export class HeaderComponent {
  menuOpen = false;

  toggleMenu() {
    this.menuOpen = !this.menuOpen; 
  }

  closeMenu() {
    this.menuOpen = false;
  }

  @Input() title: string = "Nuestro logo";

  navLinks = [
    { label: 'Noticias', path: '/noticias' },
    { label: 'Contactanos', path: '/contacto' },
    { label: 'Tus favoritos', path: '/favoritos' },
    { label: 'Publica tu historia', path: '/publica-historia' }
  ]
}
