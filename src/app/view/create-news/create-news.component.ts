import { Component, EventEmitter, OnInit, Output } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterModule, ActivatedRoute, Router } from '@angular/router';
import Swal from 'sweetalert2';
import { CATEGORIAS_NOTICIA } from '../../models/noticia.model';
import { NoticiasService } from '../../services/noticias.service';

@Component({
  selector: 'app-create-news',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  templateUrl: './create-news.component.html',
  styleUrl: './create-news.component.css'
})
export class CreateNewsComponent implements OnInit {
  categorias = CATEGORIAS_NOTICIA;

  titulo = '';
  categoria = '';
  resumen = '';
  imagen = '';

  modoEdicion = false;
  private idEdicion?: number;

  @Output() noticiaGuardada = new EventEmitter<void>();

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private noticiasService: NoticiasService
  ) {}

  async ngOnInit() {
    const idParam = this.route.snapshot.paramMap.get('id');
    if (!idParam) return;

    this.modoEdicion = true;
    this.idEdicion = Number(idParam);

    const noticia = await this.noticiasService.getById(this.idEdicion);
    if (noticia) {
      this.titulo = noticia.titulo;
      this.categoria = noticia.categoria;
      this.resumen = noticia.resumen;
      this.imagen = noticia.imagen;
    }
  }

  async guardar() {
    const datos = {
      titulo: this.titulo,
      categoria: this.categoria,
      resumen: this.resumen,
      imagen: this.imagen
    };

    if (this.modoEdicion && this.idEdicion !== undefined) {
      await this.noticiasService.update(this.idEdicion, datos);
    } else {
      await this.noticiasService.create(datos);
    }

    this.noticiaGuardada.emit();

    Swal.fire({
      title: '<span style="color: #6c8fe3;">Se ha registrado su noticia</span>',
      text: 'Se ha guardado con éxito.',
      confirmButtonText: 'Volver al inicio',
      confirmButtonColor: '#718fe2'
    }).then(() => {
      if (this.modoEdicion && this.idEdicion !== undefined) {
        this.router.navigate(['/detalle-noticia', this.idEdicion]);
      } else {
        this.limpiar();
      }
    });
  }

  limpiar() {
    this.titulo = '';
    this.categoria = '';
    this.resumen = '';
    this.imagen = '';
  }
}
