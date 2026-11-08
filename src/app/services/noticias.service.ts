import { Injectable } from '@angular/core';
import { Noticia } from '../models/noticia.model';

@Injectable({ providedIn: 'root' })
export class NoticiasService {
  private readonly CLAVE_STORAGE = 'noticias';
  private noticias: Noticia[] = [];
  private listo: Promise<void>;

  constructor() {
    this.listo = this.inicializar();
  }

  private async inicializar(): Promise<void> {
    const guardado = localStorage.getItem(this.CLAVE_STORAGE);
    if (guardado) {
      this.noticias = JSON.parse(guardado);
      return;
    }

    const respuesta = await fetch('assets/data/noticias.json');
    const datos: Array<Omit<Noticia, 'destacada'>> = await respuesta.json();
    const idsDestacadasPorDefecto = [2, 3, 4];
    this.noticias = datos.map(n => ({ ...n, destacada: idsDestacadasPorDefecto.includes(n.id) }));
    this.guardar();
  }

  private guardar(): void {
    localStorage.setItem(this.CLAVE_STORAGE, JSON.stringify(this.noticias));
  }

  async getAll(): Promise<Noticia[]> {
    await this.listo;
    return [...this.noticias];
  }

  async getById(id: number): Promise<Noticia | undefined> {
    await this.listo;
    return this.noticias.find(n => n.id === id);
  }

  async getDestacadas(): Promise<Noticia[]> {
    await this.listo;
    return this.noticias.filter(n => n.destacada);
  }

  async getCategorias(): Promise<string[]> {
    await this.listo;
    return [...new Set(this.noticias.map(n => n.categoria))];
  }

  async create(datos: Omit<Noticia, 'id' | 'destacada'>): Promise<Noticia> {
    await this.listo;
    const nuevoId = this.noticias.length ? Math.max(...this.noticias.map(n => n.id)) + 1 : 1;
    const nueva: Noticia = { id: nuevoId, destacada: false, ...datos };
    this.noticias.push(nueva);
    this.guardar();
    return nueva;
  }

  async update(id: number, cambios: Partial<Omit<Noticia, 'id'>>): Promise<void> {
    await this.listo;
    const indice = this.noticias.findIndex(n => n.id === id);
    if (indice === -1) return;
    this.noticias[indice] = { ...this.noticias[indice], ...cambios };
    this.guardar();
  }

  async delete(id: number): Promise<void> {
    await this.listo;
    this.noticias = this.noticias.filter(n => n.id !== id);
    this.guardar();
  }

  async toggleDestacada(id: number): Promise<void> {
    await this.listo;
    const noticia = this.noticias.find(n => n.id === id);
    if (noticia) {
      noticia.destacada = !noticia.destacada;
      this.guardar();
    }
  }
}
