import { Routes } from '@angular/router';
import { NoticiasComponent } from './view/noticias/noticias.component';
import { HomeComponent } from './view/home/home.component';
import { FavoritosComponent } from './view/favoritos/favoritos.component';
import { DetalleNoticiaComponent } from './view/detalle-noticia/detalle-noticia.component';
import { ContactComponent } from './view/contact/contact.component';
import { PublicaHistoriaComponent } from './view/publica-historia/publica-historia.component';
import { CreateNewsComponent } from './view/create-news/create-news.component';

export const routes: Routes = [
  { path: 'noticias', component: NoticiasComponent },
  { path: 'favoritos', component: FavoritosComponent },
  { path: 'detalle-noticia/:id', component: DetalleNoticiaComponent },
  { path: 'crear-noticia', component: CreateNewsComponent },
  { path: 'crear-noticia/:id', component: CreateNewsComponent },
  { path: 'contacto', component: ContactComponent },
  { path: 'publica-historia', component: PublicaHistoriaComponent },
  { path: '', component: HomeComponent}
];