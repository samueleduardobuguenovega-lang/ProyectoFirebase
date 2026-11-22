package com.stomas.proyectofirebase;

import android.os.Bundle;
import android.text.TextUtils;
import android.util.Log;
import android.view.View;
import android.widget.ArrayAdapter;
import android.widget.EditText;
import android.widget.ListView;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;

import com.google.firebase.firestore.FirebaseFirestore;
import com.google.firebase.firestore.QueryDocumentSnapshot;
import com.google.firebase.firestore.QuerySnapshot;
import com.google.android.gms.tasks.OnCompleteListener;
import com.google.android.gms.tasks.Task;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * Actividad 3.1 y 3.2: escritura y lectura de datos en Cloud Firestore.
 *
 * Coleccion: mascotas
 * Documento: codigo, nombre, dueno, direccion
 */
public class MainActivity extends AppCompatActivity {

    private static final String TAG = "MainActivity";
    private static final String COLECCION = "mascotas";

    private EditText edtCodigo;
    private EditText edtNombre;
    private EditText edtDueno;
    private EditText edtDireccion;

    private ListView listaMascotas;
    private final List<String> datos = new ArrayList<>();
    private ArrayAdapter<String> adaptador;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        edtCodigo = findViewById(R.id.edtCodigo);
        edtNombre = findViewById(R.id.edtNombre);
        edtDueno = findViewById(R.id.edtDueno);
        edtDireccion = findViewById(R.id.edtDireccion);

        listaMascotas = findViewById(R.id.listaMascotas);
        adaptador = new ArrayAdapter<>(this, android.R.layout.simple_list_item_1, datos);
        listaMascotas.setAdapter(adaptador);
    }

    /** Boton Enviar: agrega un documento nuevo a la coleccion mascotas. */
    public void enviarDatos(View view) {
        String codigo = edtCodigo.getText().toString().trim();
        String nombre = edtNombre.getText().toString().trim();
        String dueno = edtDueno.getText().toString().trim();
        String direccion = edtDireccion.getText().toString().trim();

        if (TextUtils.isEmpty(codigo) || TextUtils.isEmpty(nombre)
                || TextUtils.isEmpty(dueno) || TextUtils.isEmpty(direccion)) {
            Toast.makeText(this, R.string.msg_campos_vacios, Toast.LENGTH_SHORT).show();
            return;
        }

        Map<String, Object> mascota = new HashMap<>();
        mascota.put("codigo", codigo);
        mascota.put("nombre", nombre);
        mascota.put("dueno", dueno);
        mascota.put("direccion", direccion);

        FirebaseFirestore db = FirebaseFirestore.getInstance();
        db.collection(COLECCION)
                .add(mascota)
                .addOnSuccessListener(documentReference -> {
                    Log.d(TAG, "Documento creado: " + documentReference.getId());
                    Toast.makeText(MainActivity.this,
                            R.string.msg_enviado_ok, Toast.LENGTH_SHORT).show();
                    limpiarFormulario();
                })
                .addOnFailureListener(e -> {
                    Log.e(TAG, "Fallo al escribir en Firestore", e);
                    Toast.makeText(MainActivity.this,
                            getString(R.string.msg_error_enviar, String.valueOf(e.getMessage())),
                            Toast.LENGTH_SHORT).show();
                });
    }

    /** Boton Cargar lista. */
    public void CargarLista(View view) {
        cargarListaFirestore();
    }

    /** Lee la coleccion mascotas y la muestra en el ListView. */
    public void cargarListaFirestore() {
        FirebaseFirestore db = FirebaseFirestore.getInstance();

        db.collection(COLECCION)
                .get()
                .addOnCompleteListener(new OnCompleteListener<QuerySnapshot>() {
                    @Override
                    public void onComplete(@NonNull Task<QuerySnapshot> task) {
                        if (task.isSuccessful()) {
                            datos.clear();

                            for (QueryDocumentSnapshot documento : task.getResult()) {
                                String linea = "|| " + valor(documento, "codigo") + " || "
                                        + valor(documento, "nombre") + " || "
                                        + valor(documento, "dueno") + " || "
                                        + valor(documento, "direccion");
                                datos.add(linea);
                            }

                            adaptador.notifyDataSetChanged();

                            if (datos.isEmpty()) {
                                Toast.makeText(MainActivity.this,
                                        R.string.msg_lista_vacia, Toast.LENGTH_SHORT).show();
                            }
                        } else {
                            Log.e(TAG, "Error al obtener datos de Firestore", task.getException());
                            Toast.makeText(MainActivity.this,
                                    getString(R.string.msg_error_leer,
                                            String.valueOf(task.getException() == null
                                                    ? "" : task.getException().getMessage())),
                                    Toast.LENGTH_SHORT).show();
                        }
                    }
                });
    }

    /** Devuelve el campo como texto, sin romper la lista si viene nulo. */
    private String valor(QueryDocumentSnapshot documento, String campo) {
        String texto = documento.getString(campo);
        return texto == null ? "" : texto;
    }

    private void limpiarFormulario() {
        edtCodigo.setText("");
        edtNombre.setText("");
        edtDueno.setText("");
        edtDireccion.setText("");
        edtCodigo.requestFocus();
    }
}
