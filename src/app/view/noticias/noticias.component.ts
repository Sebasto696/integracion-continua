import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { CardNoticiaComponent } from '../../components/card-noticia/card-noticia.component';
import { Noticia } from '../../models/noticia.model';
import { NoticiasService } from '../../services/noticias.service';

@Component({
  selector: 'app-noticias',
  standalone: true,
  imports: [CommonModule, FormsModule, CardNoticiaComponent],
  templateUrl: './noticias.component.html',
  styleUrl: './noticias.component.css'
})
export class NoticiasComponent implements OnInit {
  noticias: Noticia[] = [];
  categorias: string[] = [];

  busqueda: string = '';
  categoriaSeleccionada: string = '';

  paginaActual: number = 1;
  porPagina: number = 6;

  constructor(private noticiasService: NoticiasService) {}

  async ngOnInit() {
    this.noticias = await this.noticiasService.getAll();
    this.categorias = await this.noticiasService.getCategorias();
  }

  async onToggleDestacada(id: number) {
    await this.noticiasService.toggleDestacada(id);
    this.noticias = await this.noticiasService.getAll();
  }

  get noticiasFiltradas(): Noticia[] {
    return this.noticias.filter(n => {
      const coincideNombre = n.titulo.toLowerCase().includes(this.busqueda.toLowerCase());
      const coincideCategoria = this.categoriaSeleccionada
        ? n.categoria === this.categoriaSeleccionada
        : true;
      return coincideNombre && coincideCategoria;
    });
  }

  get totalPaginas(): number {
    return Math.max(1, Math.ceil(this.noticiasFiltradas.length / this.porPagina));
  }

  get noticiasPagina(): Noticia[] {
    const inicio = (this.paginaActual - 1) * this.porPagina;
    return this.noticiasFiltradas.slice(inicio, inicio + this.porPagina);
  }

  get paginasArray(): number[] {
    return Array.from({ length: this.totalPaginas }, (_, i) => i + 1);
  }

  irAPagina(pagina: number) {
    if (pagina >= 1 && pagina <= this.totalPaginas) {
      this.paginaActual = pagina;
    }
  }

  reiniciarPagina() {
    this.paginaActual = 1;
  }
}