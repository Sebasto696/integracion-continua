import { Injectable } from '@angular/core';
import Swal from 'sweetalert2';
import { Noticia } from '../models/noticia.model';

interface NoticiaApi {
  id: number;
  titulo: string;
  contenido: string;
  imagen_url: string | null;
  categoria: string;
  destacado: boolean;
}

type DatosNoticia = Omit<Noticia, 'id' | 'destacada'>;

@Injectable({ providedIn: 'root' })
export class NoticiasService {
  private readonly API = '/api/noticias';

  private aNoticia(noticia: NoticiaApi): Noticia {
    return {
      id: noticia.id,
      titulo: noticia.titulo,
      imagen: noticia.imagen_url ?? '',
      categoria: noticia.categoria,
      resumen: noticia.contenido,
      destacada: noticia.destacado
    };
  }

  private aCuerpo(datos: DatosNoticia): string {
    return JSON.stringify({
      titulo: datos.titulo,
      contenido: datos.resumen,
      imagen_url: datos.imagen,
      categoria: datos.categoria
    });
  }

  private fallo(mensaje: string): Error {
    Swal.fire({
      title: 'No se pudo completar la acción',
      text: mensaje,
      icon: 'error',
      confirmButtonColor: '#718fe2'
    });
    return new Error(mensaje);
  }

  private async peticion<T>(ruta: string, opciones: RequestInit = {}, nuloSi404 = false): Promise<T> {
    let respuesta: Response;
    try {
      respuesta = await fetch(`${this.API}${ruta}`, {
        ...opciones,
        headers: opciones.body ? { 'Content-Type': 'application/json' } : undefined
      });
    } catch {
      throw this.fallo('No fue posible conectar con el servidor.');
    }

    if (respuesta.status === 404 && nuloSi404) return null as T;
    if (respuesta.status === 204) return undefined as T;

    const cuerpo = await respuesta.json().catch(() => null);
    if (!respuesta.ok) {
      throw this.fallo(cuerpo?.error ?? 'No fue posible completar la operación.');
    }
    return cuerpo as T;
  }

  async getAll(): Promise<Noticia[]> {
    const noticias = await this.peticion<NoticiaApi[]>('');
    return noticias.map(n => this.aNoticia(n));
  }

  async getById(id: number): Promise<Noticia | undefined> {
    const noticia = await this.peticion<NoticiaApi | null>(`/${id}`, {}, true);
    return noticia ? this.aNoticia(noticia) : undefined;
  }

  async getDestacadas(): Promise<Noticia[]> {
    return (await this.getAll()).filter(n => n.destacada);
  }

  async getCategorias(): Promise<string[]> {
    return [...new Set((await this.getAll()).map(n => n.categoria))];
  }

  async create(datos: DatosNoticia): Promise<Noticia> {
    const noticia = await this.peticion<NoticiaApi>('', { method: 'POST', body: this.aCuerpo(datos) });
    return this.aNoticia(noticia);
  }

  async update(id: number, datos: DatosNoticia): Promise<void> {
    await this.peticion<NoticiaApi>(`/${id}`, { method: 'PUT', body: this.aCuerpo(datos) });
  }

  async delete(id: number): Promise<void> {
    await this.peticion<void>(`/${id}`, { method: 'DELETE' });
  }

  async toggleDestacada(id: number): Promise<void> {
    const noticia = await this.getById(id);
    if (!noticia) return;

    await this.peticion<NoticiaApi>(`/${id}/destacado`, {
      method: 'PATCH',
      body: JSON.stringify({ destacado: !noticia.destacada })
    });
  }
}
