import arcpy
import glob
import os
import arcpy.cartography as CA
from arcpy import env
from multiprocessing import Pool


#### Elimina ruidos
#
#
# Autores:
#
# Codigo: Daniel Grabert Baranjak
# 
# Geoprocessamento:
#
# Aline Kaziuk



def filtro(gdb_entrada,gdb_processamento,cidade,Shape_agricultura):

	print("Processando ", cidade, " ...")


	# Variaveis ##############
	arcpy.env.workspace = gdb_entrada
	arcpy.env.processamento = gdb_processamento

	##########################

	# Decidimos fazer este processo no final
	#### Sql gridcode IN (1, 4, 5, 6, 8)
	#	print("Definition query...")
	#	# Process: Iterate Feature Selection
	#	#  ENTRADA: gdb_entrada + \ + cidade
	#	entrada_iterate = arcpy.env.workspace + "\\" + cidade
	#	arcpy.IterateFeatureSelection_mb(entrada_iterate, fields="MUNICIPIO #", skip_nulls="false")


	print("Clipando..")

	saida_clip = cidade + "_Clip"
	arcpy.Clip_analysis(cidade, Shape_agricultura , saida_clip) # vamos clipar


	print("Erase...")

	saida_erase = arcpy.env.processamento + "\\" + cidade + "_Erase"

	#Erase_analysis (in_features, erase_features, out_feature_class, {cluster_tolerance})
	arcpy.Erase_analysis(saida_clip, Shape_agricultura , saida_erase)


	print("Append...")

	# Vamos juntar o featureclass com o mask

	#			Input , target , schema
	arcpy.Append_management(saida_erase,saida_clip,"NO_TEST")


	print("Multipart to single part...")

	saida_singlepart = cidade + "_SinglePart"
	# 	MultipartToSinglepart_management (in_features, out_feature_class)
	arcpy.MultipartToSinglepart_management(saida_clip,saida_singlepart)

	print("Feature class to feature class...")

	saida_featureclass = cidade + "_FeatureClass"

	delimitedField = arcpy.AddFieldDelimiters(arcpy.env.workspace, "Shape_Area")
	expressaum = delimitedField + " > 3000" # Queremos as areas de shape maiores que 3000, consulta SQL
	#	FeatureClassToFeatureClass_conversion (in_features, out_path, out_name, {where_clause}, {field_mapping}, {config_keyword})
	arcpy.FeatureClassToFeatureClass_conversion(saida_singlepart, arcpy.env.processamento,saida_featureclass,expressaum)


	print("Simplify polygon...")

	entrada_simplify = arcpy.env.processamento + "\\" + saida_featureclass

	tolerancia = "10 Meters"
	area_minima = "30 Hectares"

	saida_simplify = arcpy.env.processamento + "\\" + cidade + "_SimplifyPolygon"
	#	SimplifyPolygon_cartography (in_features, out_feature_class, algorithm, tolerance, {minimum_area}, {error_option}, {collapsed_point_option})
	CA.SimplifyPolygon(entrada_simplify, saida_simplify, "WEIGHTED_AREA", tolerancia, area_minima, "#", "NO_KEEP")



	return


# 	Inicio do programa
if __name__ == "__main__":

#
#
#       MUITO CUIDADO!!!!
#
#   O gdb deve ter sempre uma FEATURE com o mesmo nome da cidade + _agr, exemplo: ALTOGARCAS (cidade) -> ALTOGARCAS_agr
#
#
#
    arcpy.env.workspace = "querencia.gdb"  # GEO DATABASE ENTRADA
    processamento = "processamento_nordeste.gdb"    #GEO DATABASE PROCESSAMENTO

    datasets = arcpy.ListDatasets(feature_type='feature')
    datasets = [''] + datasets if datasets is not None else []
    
    cidades = []

    for ds in datasets:
        for fc in arcpy.ListFeatureClasses(feature_dataset=ds):
            if fc[-4:] != "_agr":
                cidades.append(fc)

    print ("Vamos filtrar as seguintes cidades:")
    for cidade in cidades:
        shape = cidade + "_agr"
        print("Cidade: ",cidade," Feature Agricultura ",shape)

    # Vamos passar o filtro de ..... na cidade Alto garcas
    for cidade in cidades:
        shape = cidade.lower() + "_agr" ## lower gambiarra -> mudar
        filtro(arcpy.env.workspace ,processamento,cidade,shape)


    # depois de filtrar todos municipios, fazer append de todas areas
    #...
    # intersect com shape de municipios do estado
    # dissolve 
