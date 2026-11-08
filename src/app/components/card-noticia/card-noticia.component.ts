import { CommonModule } from '@angular/common';
import { Component, EventEmitter, Input, Output } from '@angular/core';
import { RouterModule } from '@angular/router';

@Component({
  selector: 'app-card-noticia',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './card-noticia.component.html',
  styleUrl: './card-noticia.component.css'
})

export class CardNoticiaComponent {
  @Input({ required: true, alias: 'id' }) id!: number;
  @Input({ required: true, alias: 'titulo' }) titulo = '';
  @Input({ required: true, alias: 'imagen' }) imagen = '';
  @Input({ required: true, alias: 'resumen' }) resumen = '';
  @Input({ alias: 'destacada' }) destacada = false;
  @Input({ alias: 'mostrarBotonDestacada' }) mostrarBotonDestacada = true;

  @Output() toggleDestacada = new EventEmitter<number>();
}
