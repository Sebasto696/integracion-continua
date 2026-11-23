export interface Noticia {
  id: number;
  titulo: string;
  imagen: string;
  categoria: string;
  resumen: string;
  destacada: boolean;
}

export const CATEGORIAS_NOTICIA: string[] = ['Institucional', 'Deportes', 'Cultura', 'Tecnología'];
