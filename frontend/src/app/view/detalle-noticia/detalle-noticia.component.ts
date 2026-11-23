import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import Swal from 'sweetalert2';
import { Noticia } from '../../models/noticia.model';
import { NoticiasService } from '../../services/noticias.service';

@Component({
  selector: 'app-detalle-noticia',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './detalle-noticia.component.html',
  styleUrl: './detalle-noticia.component.css'
})
export class DetalleNoticiaComponent implements OnInit {
  noticia?: Noticia;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private noticiasService: NoticiasService
  ) {}

  async ngOnInit() {
    const id = Number(this.route.snapshot.paramMap.get('id'));
    this.noticia = await this.noticiasService.getById(id);
  }

  editar() {
    if (this.noticia) {
      this.router.navigate(['/crear-noticia', this.noticia.id]);
    }
  }

  async toggleDestacada() {
    if (!this.noticia) return;
    await this.noticiasService.toggleDestacada(this.noticia.id);
    this.noticia = await this.noticiasService.getById(this.noticia.id);
  }

  eliminar() {
    if (!this.noticia) return;

    Swal.fire({
      title: '¿Eliminar esta noticia?',
      text: 'Esta acción no se puede deshacer.',
      icon: 'warning',
      showCancelButton: true,
      confirmButtonText: 'Eliminar',
      cancelButtonText: 'Cancelar',
      confirmButtonColor: '#718fe2'
    }).then(resultado => {
      if (resultado.isConfirmed && this.noticia) {
        this.noticiasService.delete(this.noticia.id).then(() => {
          this.router.navigate(['/noticias']);
        });
      }
    });
  }
}
