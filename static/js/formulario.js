// formulario.js - Script exclusivo para la página de formulario
document.addEventListener('DOMContentLoaded', function() {

    // Elementos del DOM
    const btnEdit = document.getElementById('btnEdit');
    const formularioFallecido = document.getElementById('formularioFallecido');
    const formSection = document.getElementById('formSection');

    // Establecer fecha y hora actual
    function setFechaHoraActual() {
        const ahora = new Date();
        const year = ahora.getFullYear();
        const month = String(ahora.getMonth() + 1).padStart(2, '0');
        const day = String(ahora.getDate()).padStart(2, '0');
        const hours = String(ahora.getHours()).padStart(2, '0');
        const minutes = String(ahora.getMinutes()).padStart(2, '0');
        
        document.getElementById('fechaHoraIngreso').value = `${year}-${month}-${day}T${hours}:${minutes}`;
    }

    // Calcular edad
    document.getElementById('fechaNacimiento').addEventListener('change', function() {
        const fechaNacimiento = new Date(this.value);
        const hoy = new Date();
        
        let edad = hoy.getFullYear() - fechaNacimiento.getFullYear();
        const mes = hoy.getMonth() - fechaNacimiento.getMonth();
        
        if (mes < 0 || (mes === 0 && hoy.getDate() < fechaNacimiento.getDate())) {
            edad--;
        }
        
        document.getElementById('edad').value = edad + ' AÑOS';
    });

    // Llenar formulario con datos extraídos
    function llenarFormularioConDatos(datos) {
        console.log('Llenando formulario con:', datos);
        
        // Rellenar campos
        if (datos.primerApellido) document.getElementById('primerApellido').value = datos.primerApellido;
        if (datos.segundoApellido) document.getElementById('segundoApellido').value = datos.segundoApellido;
        if (datos.prenombres) document.getElementById('prenombres').value = datos.prenombres;
        
        // Fecha de nacimiento - convertir formato si es necesario
        if (datos.fechaNacimiento) {
            let fechaFormateada = datos.fechaNacimiento;
            
            // Si viene en formato "DD MM YYYY", convertir a "YYYY-MM-DD"
            if (datos.fechaNacimiento.includes(' ')) {
                const partes = datos.fechaNacimiento.split(' ');
                if (partes.length === 3) {
                    fechaFormateada = `${partes[2]}-${partes[1].padStart(2, '0')}-${partes[0].padStart(2, '0')}`;
                }
            }
            
            document.getElementById('fechaNacimiento').value = fechaFormateada;
            // Calcular edad
            document.getElementById('fechaNacimiento').dispatchEvent(new Event('change'));
        }
        
        // Edad directa si viene del backend
        if (datos.edad) {
            document.getElementById('edad').value = datos.edad + ' AÑOS';
        }
        
        if (datos.tipoDocumento) document.getElementById('tipoDocumento').value = datos.tipoDocumento;
        if (datos.numeroDocumento) document.getElementById('numeroDocumento').value = datos.numeroDocumento;
        if (datos.sexo) document.getElementById('sexo').value = datos.sexo;
        if (datos.estadoCivil) document.getElementById('estadoCivil').value = datos.estadoCivil.toUpperCase();
        if (datos.gradoInstruccion) document.getElementById('gradoInstruccion').value = datos.gradoInstruccion;
        
        // Marcar campos como auto-completados
        document.querySelectorAll('.form-group input:not([disabled]), .form-group select').forEach(field => {
            if (field.value && field.id !== 'tipoDocumento') {
                field.classList.add('auto-filled');
            }
        });
        
        // Deshabilitar campos (modo solo lectura)
        deshabilitarCampos();
        
        // Mostrar formulario
        formSection.classList.add('active');
    }

    // Habilitar/deshabilitar campos
    function deshabilitarCampos() {
        document.querySelectorAll('.form-group input:not([disabled]), .form-group select').forEach(field => {
            field.disabled = true;
        });
        if (btnEdit) btnEdit.disabled = false;
    }

    function habilitarCampos() {
        document.querySelectorAll('.form-group input:not(#edad):not(#fechaHoraIngreso), .form-group select').forEach(field => {
            field.disabled = false;
        });
    }

    // Botón editar
    let editMode = false;
    if (btnEdit) {
        btnEdit.addEventListener('click', () => {
            if (!editMode) {
                habilitarCampos();
                btnEdit.textContent = '✓ TERMINAR EDICIÓN';
                editMode = true;
            } else {
                deshabilitarCampos();
                btnEdit.textContent = '✎ EDITAR';
                editMode = false;
            }
        });
    }

    // Envío del formulario
    if (formularioFallecido) {
        formularioFallecido.addEventListener('submit', (e) => {
            e.preventDefault();
            
            const formData = {
                primerApellido: document.getElementById('primerApellido').value,
                segundoApellido: document.getElementById('segundoApellido').value,
                prenombres: document.getElementById('prenombres').value,
                fechaNacimiento: document.getElementById('fechaNacimiento').value,
                edad: document.getElementById('edad').value,
                tipoDocumento: document.getElementById('tipoDocumento').value,
                numeroDocumento: document.getElementById('numeroDocumento').value,
                sexo: document.getElementById('sexo').value,
                estadoCivil: document.getElementById('estadoCivil').value,
                gradoInstruccion: document.getElementById('gradoInstruccion').value,
                fechaHoraIngreso: document.getElementById('fechaHoraIngreso').value
            };
            
            console.log('Datos guardados:', formData);
            alert('✓ REGISTRO GUARDADO EXITOSAMENTE\n\nPuedes ver los datos en la consola del navegador (F12)');
            
            // Aquí enviarías los datos al servidor para guardar en base de datos
            // fetch('/api/guardar-registro', {
            //     method: 'POST',
            //     headers: { 'Content-Type': 'application/json' },
            //     body: JSON.stringify(formData)
            // });
        });
    }

    // Inicializar
    setFechaHoraActual();

    // Cargar datos desde sessionStorage si existen
    const datosGuardados = sessionStorage.getItem('datosExtraidos');
    if (datosGuardados) {
        const datos = JSON.parse(datosGuardados);
        llenarFormularioConDatos(datos);
        // Limpiar sessionStorage después de cargar
        sessionStorage.removeItem('datosExtraidos');
    }

}); // Fin del DOMContentLoaded