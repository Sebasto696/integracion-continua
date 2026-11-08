import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { RouterModule } from '@angular/router';
import { Noticia } from '../../models/noticia.model';
import { NoticiasService } from '../../services/noticias.service';

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './home.component.html',
  styleUrl: './home.component.css'
})
export class HomeComponent implements OnInit {
  noticiaPrincipal?: Noticia;
  noticiasSecundarias: Noticia[] = [];

  constructor(private noticiasService: NoticiasService) {}

  async ngOnInit() {
    await this.cargar();
  }

  private async cargar() {
    const noticias = await this.noticiasService.getAll();
    if (noticias.length > 0) {
      this.noticiaPrincipal = noticias[0];
    }
    this.noticiasSecundarias = (await this.noticiasService.getDestacadas()).slice(0, 3);
  }

  async onToggleDestacada(id: number) {
    await this.noticiasService.toggleDestacada(id);
    await this.cargar();
  }
}
