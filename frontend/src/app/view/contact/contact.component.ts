import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import {
  ReactiveFormsModule,
  FormGroup,
  FormControl,
  Validators,
  AbstractControl,
  ValidationErrors,
  ValidatorFn
} from '@angular/forms';
import Swal from 'sweetalert2';

// Validar que los correos electrónicos coincidan
const emailsMatchValidator: ValidatorFn = (
  control: AbstractControl
): ValidationErrors | null => {

  const correo = control.get('correo')?.value;
  const confirmarCorreo = control.get('confirmarCorreo')?.value;

  if (!correo || !confirmarCorreo) {
    return null;
  }

  return correo === confirmarCorreo
    ? null
    : { emailsNotMatch: true };
};

@Component({
  selector: 'app-contact',
  standalone: true,
  imports: [CommonModule, RouterModule, ReactiveFormsModule],
  templateUrl: './contact.component.html',
  styleUrl: './contact.component.css'
})
export class ContactComponent {

  // Formulario y validaciones
  contactForm = new FormGroup({

    nombre: new FormControl('', [
      Validators.required,
      Validators.minLength(2),
      Validators.pattern(/^[\p{L}\s'-]+$/u)
    ]),

    apellido: new FormControl('', [
      Validators.required,
      Validators.minLength(2),
      Validators.pattern(/^[\p{L}\s'-]+$/u)
    ]),

    direccion: new FormControl('', [
      Validators.required,
      Validators.minLength(5)
    ]),

    municipio: new FormControl('', [
      Validators.required,
      Validators.pattern(/^[\p{L}\s'-]+$/u)
    ]),

    departamento: new FormControl('', [
      Validators.required,
      Validators.pattern(/^[\p{L}\s'-]+$/u)
    ]),

    correo: new FormControl('', [
      Validators.required,
      Validators.email
    ]),

    confirmarCorreo: new FormControl('', [
      Validators.required,
      Validators.email
    ]),

    mensaje: new FormControl('', [
      Validators.required,
      Validators.minLength(10),
      Validators.maxLength(500)
    ])

  }, {
    validators: emailsMatchValidator
  });

  // Método para enviar la información
  sendingOfInformation() {

    if (this.contactForm.invalid) {
      this.contactForm.markAllAsTouched();
      return;
    }

    Swal.fire({
      title: '<span style="color: #6c8fe3;">Solicitud de mensaje</span>',
      text: 'Tu mensaje se ha enviado con éxito.',
      icon: 'success',
      confirmButtonText: 'Volver al inicio',
      confirmButtonColor: '#718fe2'
    }).then((result) => {

      if (result.isConfirmed) {
        this.clearForm();
      }

    });
  }

  // Método para limpiar el formulario
  clearForm() {
    this.contactForm.reset();
    this.contactForm.markAsUntouched();
    this.contactForm.markAsPristine();
  }

}