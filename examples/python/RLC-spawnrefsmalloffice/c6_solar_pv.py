import pvlib
from pvlib import pvsystem
import pandas as pd 

coordinates = [(42.8, -88.0, 'Chicago', 182, 'Etc/GMT+6')]         


def get_pv_output(temp_air,dni,dhi,ghi,w_sp,no_of_modules,surface_tilt,azimuth):
     energies = {}
     if temp_air<-10:
          temp_air= -10

     sandia_modules = pvlib.pvsystem.retrieve_sam('SandiaMod')

     # print ("Sandia modules: {}".format(sandia_modules))
     sapm_inverters = pvlib.pvsystem.retrieve_sam('cecinverter')
     module = sandia_modules['Canadian_Solar_CS5P_220M___2009_']
     inverter = sapm_inverters['ABB__MICRO_0_25_I_OUTD_US_208__208V_']
     temperature_model_parameters = pvlib.temperature.TEMPERATURE_MODEL_PARAMETERS['sapm']['open_rack_glass_glass']
     

     tmys = []
     for location in coordinates:
          latitude, longitude, name, altitude, timezone = location
          weather = pvlib.iotools.get_pvgis_tmy(latitude, longitude,
                                                  map_variables=True)[0]
          weather = weather.iloc[0:1]
          weather.index.name = "utc_time"
          tmys.append(weather)

     # print ("Weather Check")
     # print (weather)
     
     system = {'module': module, 'inverter': inverter,'surface_azimuth': azimuth}    

     weather['dni'] = dni
     weather['ghi'] = ghi
     weather['dhi'] = dhi
     weather['wind_speed'] = w_sp
     weather['temp_air'] = temp_air

     for location, weather in zip(coordinates, tmys):
          latitude, longitude, name, altitude, timezone = location
          system['surface_tilt'] = surface_tilt
          solpos = pvlib.solarposition.get_solarposition(
               time=weather.index,
               latitude=latitude,
               longitude=longitude,
               altitude=altitude, 
               temperature=weather["temp_air"],
               pressure=pvlib.atmosphere.alt2pres(altitude),
          )
          dni_extra = pvlib.irradiance.get_extra_radiation(weather.index)
          airmass = pvlib.atmosphere.get_relative_airmass(solpos['apparent_zenith'])
          pressure = pvlib.atmosphere.alt2pres(altitude)
          am_abs = pvlib.atmosphere.get_absolute_airmass(airmass, pressure)
          aoi = pvlib.irradiance.aoi(
               system['surface_tilt'],
               system['surface_azimuth'],
               solpos["apparent_zenith"],
               solpos["azimuth"],
          )
          total_irradiance = pvlib.irradiance.get_total_irradiance(
               system['surface_tilt'],
               system['surface_azimuth'],
               solpos['apparent_zenith'],
               solpos['azimuth'],
               weather['dni'],
               weather['ghi'],
               weather['dhi'],
               dni_extra=dni_extra,
               model='haydavies',
          )
          cell_temperature = pvlib.temperature.sapm_cell(
               total_irradiance['poa_global'],
               weather["temp_air"],
               weather["wind_speed"],
               **temperature_model_parameters,
          )
          effective_irradiance = pvlib.pvsystem.sapm_effective_irradiance(
               total_irradiance['poa_direct'],
               total_irradiance['poa_diffuse'],
               am_abs,
               aoi,
               module,
          )
          dc = pvlib.pvsystem.sapm(effective_irradiance, cell_temperature, module)
          ac = pvlib.inverter.sandia(dc['v_mp'], dc['p_mp'], inverter)

          if ac[0]<0:
               ac[0]=0

          return ac[0]*no_of_modules


def get_total_pv(temp_air,dni,dhi,ghi,w_sp):
     south_pv = get_pv_output(temp_air=temp_air,
                              dni=dni,
                              dhi=dhi,
                              ghi=ghi,
                              w_sp=w_sp,
                              no_of_modules=84,
                              surface_tilt=46,
                              azimuth=180)

     # east_pv = get_pv_output(temp_air=temp_air,
     #                          dni=dni,
     #                          dhi=dhi,
     #                          ghi=ghi,
     #                          w_sp=w_sp,
     #                          no_of_modules=59,
     #                          surface_tilt=19,
     #                          azimuth=90)

     # west_pv = get_pv_output(temp_air=temp_air,
     #                          dni=dni,
     #                          dhi=dhi,
     #                          ghi=ghi,
     #                          w_sp=w_sp,
     #                          no_of_modules=59,
     #                          surface_tilt=19,
     #                          azimuth=270)

     # north_pv = get_pv_output(temp_air=temp_air,
     #                          dni=dni,
     #                          dhi=dhi,
     #                          ghi=ghi,
     #                          w_sp=w_sp,
     #                          no_of_modules=84,
     #                          surface_tilt=46,
     #                          azimuth=0)

     car_port_pv = get_pv_output(temp_air=temp_air,
                    dni=dni,
                    dhi=dhi,
                    ghi=ghi,
                    w_sp=w_sp,
                    no_of_modules=400,
                    surface_tilt=35,
                    azimuth=180)


     total_pv = south_pv+car_port_pv 
     # total_pv= total_pv+ north_pv+east_pv+west_pv

     return total_pv 


def get_total_pv_precal(day_no,i):
     pv_df = pd.read_pickle("RL_Data/00_General/01_PV/"+str(day_no)+".pkl")
     pv_df.reset_index(drop=True,inplace=True)
     south_pv = pv_df.iloc[i].south_pv
     east_pv = pv_df.iloc[i].east_pv
     west_pv = pv_df.iloc[i].west_pv
     car_port_pv = pv_df.iloc[i].south_pv

     n_south = 84
     n_east = 59
     n_west = 59
     n_car_port = 300 #int(500/1.7)

     return n_south*south_pv + n_east*east_pv + n_west*west_pv + n_car_port*car_port_pv
















