import opyplus as op
import pandas as pd
import numpy as np
import os
import shutil
import warnings
warnings.filterwarnings("ignore") #ignore pandas warnings in opyplus.


class FromEplus():

    def __init__(self,
                 resources_dir,
                 testcase,
                 start_year="2017",
                 num_years = 3,
                 period=3600,
                 debug = False):
        '''Initialize the data index and data frame

        Parameters
        ----------
        resources_dir: string
            path to test case Resources directory
        start_time: string, default is "20170101 00:00:00"
            Pandas date-time indicating the starting
            time of the data frame.
        final_time: string, default is "20200101 00:00:00"
            Pandas date-time indicating the end time
            of the data frame.
        period: integer, default is 3600
            Number of seconds of the sampling time.

        '''
        self.debug = debug
        self.testcase = testcase

        self.start_year = start_year
        self.num_years = num_years
        self.resources_dir = os.path.join(resources_dir, testcase)
        self.period = period

        # search for weather file and IDF
        for file in os.listdir(self.resources_dir):
            if file.endswith('.epw'):
                self.weapath = os.path.join(self.resources_dir, file)
            if file.endswith('.idf'):
                self.idfpath = os.path.join(self.resources_dir, file)
                self.modidfpath = os.path.join(self.resources_dir, 'mod_' + file)
        self.tempPath = os.path.join(self.resources_dir, 'temp')

        try:
            os.mkdir(self.tempPath)
        except:
            shutil.rmtree(self.tempPath)
            os.mkdir(self.tempPath)

        assert hasattr(self, 'weapath'), "Error: no EPW weather files found in {}".format(self.resources_dir)
        assert hasattr(self, 'idfpath'), "Error: no IDF files found in {}".format(self.resources_dir)

        # Create a date time index
        self.datetime_index = pd.date_range(
            start=pd.Timestamp(start_year + "0101 00:00:00"),
            end=pd.Timestamp(str(int(start_year) + num_years -1) + "1231 23:00:00"),
            freq='{period}s'.format(period=period))

        # Get an absolute time vector in seconds and save it
        time_since_epoch = self.datetime_index.asi8 / 1e9
        self.time = time_since_epoch - time_since_epoch[0]

        # load epmodel
        self.epm = op.Epm.load(self.idfpath)
        # set output to CSV format
        try:
            self.epm.OutputControl_Table_Style[0].column_separator = 'comma'
        except IndexError:
            self.epm.OutputControl_Table_Style.add(column_separator='comma')
        self.epm.set_comment('Modified for spawn')
        # save and reload
        self.epm.save(self.modidfpath)
        self.epm = op.Epm.load(self.modidfpath)

    def generateAllData(self):
        print("Finding zone names...")
        self.getZones()
        print("OK.\nGenerating weather.csv...")
        self.generate_weather()

        print("OK.\nGenerating emissions.csv...")
        self.generate_emissions()
        print("OK.\nGenerating dataFromModel.csv...")
        self.generate_summaries()
        print("OK.\nGenerating prices.csv...")
        self.generate_prices()
        self.generateModelData()
        print("OK.\nAll resources successfully generated!\nCleaning up...")
        self.cleanup()
        print("OK.\nThe Spawn resource files can be found in {}".format(self.resources_dir))

    def cleanup(self):
        if os.path.isdir(self.tempPath):
            shutil.rmtree(self.tempPath)
        for file in os.listdir(self.resources_dir):
            if file.startswith('mod_') and file.endswith('.idf'):
                os.remove(os.path.join(self.resources_dir, file))

    def generateModelData(self):
        dataframe = pd.DataFrame(index=self.datetime_index)
        extrasdataframe = pd.DataFrame(index=self.datetime_index)
        extrasdataframe['time'] = self.time
        dataframe['time'] = self.time
        self.getZones()
        occdf = self.generateOccupancy()
        gainsdf = self.generateGains()
        setpdf = self.generateSetpoints()

        dataframe = pd.concat([dataframe, occdf, gainsdf, setpdf], axis=1)
        for zone in self.zones:
            dataframe['InternalGainsCon[{}]'.format(zone)] = dataframe['LightsInternalGainsCon[{}]'.format(zone)] \
                                                             + dataframe['EquipInternalGainsCon[{}]'.format(zone)] \
                                                             + dataframe['PeopleInternalGainsCon[{}]'.format(zone)]
            dataframe['InternalGainsRad[{}]'.format(zone)] = dataframe['LightsInternalGainsRad[{}]'.format(zone)] \
                                                             + dataframe['EquipInternalGainsRad[{}]'.format(zone)] \
                                                             + dataframe['PeopleInternalGainsRad[{}]'.format(zone)]
            dataframe['InternalGainsLat[{}]'.format(zone)] = dataframe['EquipInternalGainsLat[{}]'.format(zone)] \
                                                             + dataframe['PeopleInternalGainsLat[{}]'.format(zone)]

            extrasdataframe['ElecLoads[{}]'.format(zone)] = dataframe['LightsInternalGainsCon[{}]'.format(zone)] \
                                                            + dataframe['EquipInternalGainsCon[{}]'.format(zone)] \
                                                            + dataframe['LightsInternalGainsRad[{}]'.format(zone)] \
                                                            + dataframe['EquipInternalGainsRad[{}]'.format(zone)] \
                                                            + dataframe['EquipInternalGainsLat[{}]'.format(zone)]

            drop = ['LightsInternalGainsCon[{}]'.format(zone), 'EquipInternalGainsCon[{}]'.format(zone),
                            'PeopleInternalGainsCon[{}]'.format(zone), 'LightsInternalGainsRad[{}]'.format(zone),
                            'EquipInternalGainsRad[{}]'.format(zone), 'PeopleInternalGainsRad[{}]'.format(zone),
                            'EquipInternalGainsLat[{}]'.format(zone), 'PeopleInternalGainsLat[{}]'.format(zone)]
            dataframe.drop(columns = drop, inplace=True)



        dataframe.to_csv(os.path.join(self.resources_dir, 'dataFromModel.csv'), index=False)
        extrasdataframe.to_csv(os.path.join(self.resources_dir, 'extras.csv'), index=False)

    def generateSetpoints(self):
        setpointsDataframe = pd.DataFrame()

        for thermostat in self.epm.zonecontrol_thermostat:
            if thermostat.zone_or_zonelist_name.name in self.zones:

                setpointsDataframe['LowerSetp[{}]'.format(thermostat.zone_or_zonelist_name.name)] = self.fromEPSchedToList(
                    self.epm.Schedule_Compact.one(lambda x: x.name == thermostat.control_1_name.heating_setpoint_temperature_schedule_name.name))
                setpointsDataframe['UpperSetp[{}]'.format(thermostat.zone_or_zonelist_name.name)] = self.fromEPSchedToList(
                    self.epm.Schedule_Compact.one(
                        lambda x: x.name == thermostat.control_1_name.cooling_setpoint_temperature_schedule_name.name))
                #todo: wait for it to break when there are several control types
                setpointsDataframe['LowerSetp[{}]'.format(thermostat.zone_or_zonelist_name.name)] = \
                    setpointsDataframe['LowerSetp[{}]'.format(thermostat.zone_or_zonelist_name.name)].apply(toKelvin)
                setpointsDataframe['UpperSetp[{}]'.format(thermostat.zone_or_zonelist_name.name)] = \
                    setpointsDataframe['UpperSetp[{}]'.format(thermostat.zone_or_zonelist_name.name)].apply(toKelvin)
        while len(setpointsDataframe) <= len(self.datetime_index):
            setpointsDataframe = setpointsDataframe.append(setpointsDataframe.iloc[:168], ignore_index=True)
        setpointsDataframe = setpointsDataframe.iloc[:len(self.datetime_index)]
        setpointsDataframe.index = self.datetime_index
        return setpointsDataframe

    def generate_summaries(self):
        # simulate the model to fetch autocalculated outputs
        if not hasattr(self, 'wea'):
            self.generate_weather()
        s = op.simulate(self.epm, self.wea, self.tempPath)
        if s.get_status() == "finished" and self.debug == True:
            print("Debug: IDF file OK")
        elif s.get_status() != "finished":
            raise ValueError("Error: simulation returned with status ", s.get_status())

        self.eio, self.summary = find_eio_and_summary_table(self.tempPath)

    def generate_weather(self):

        self.wea = op.WeatherData.load(self.weapath)
        wea = self.wea.get_weather_series()
        weatherData = pd.concat([wea]*self.num_years, ignore_index=True)
        weatherData.index = self.datetime_index
        weatherData['time'] = self.time
        drop = ['year','month','day','hour','minute','datasource', 'glohorillum', 'dirnorillum', 'difhorillum', 'zenlum', \
        'visibility', 'presweathobs', 'presweathcodes', 'precip_wtr', 'aerosol_opt_depth', 'snowdepth', 'days_last_snow', \
        'Albedo', 'liq_precip_depth', 'liq_precip_rate', 'horirsky', 'extdirrad']
        weatherData.drop(columns=drop, axis=0, inplace=True)

        newColumns = {'drybulb' : 'TDryBul',
                      'dewpoint' : 'TDewPoi',
                      'relhum' : 'relHum',
                      'atmos_pressure': 'pAtm',
                      'dirnorrad': 'HDirNor',
                      'glohorrad': 'HGloHor',
                      'difhorrad': 'HDifHor',
                      'winddir': 'winDir',
                      'windspd': 'winSpe',
                      'ceiling_hgt' : 'ceiHei',
                      'totskycvr': 'nTot',
                      'opaqskycvr': 'nOpa',
                      'exthorrad': 'HHorIR',
                      }# needed to comply with categories.json
        weatherData.rename(columns=newColumns, inplace=True)
        weatherData.to_csv(os.path.join(self.resources_dir, 'weather.csv'), index=False)

    def generate_emissions(self):

        # GWP100 (AR5) values from February 2016

        GWP = {'CH4' : 28,
               'N20' : 265
               }
        emissions = pd.DataFrame(index=self.datetime_index)
        emissions['time'] = self.time

        for fuel in self.epm.FuelFactors:
            if fuel.existing_fuel_resource_name == 'electricity':
                # In the IDF, values are in g/MJ. We convert to kg/kWh and apply the CO2-eq
                name = 'EmissionsElectricPower'
            elif fuel.existing_fuel_resource_name == 'naturalgas':
                name = 'EmissionsGasPower'
            else:
                name = None
            if name is not None:
                emissions[name] = [(fuel.co2_emission_factor / 3600
                                    + fuel.ch4_emission_factor * GWP['CH4'] / 3600
                                    + fuel.n2o_emission_factor * GWP['N20'] / 3600)
                                    * fuel.source_energy_factor        # apply the source conversion
                                    for i in range(len(emissions['time']))] # constant for now
        cols = emissions.columns
        assert ('EmissionsElectricPower' in cols and 'EmissionsGasPower' in cols), "Error: could not generate" \
                                                                                   "emissions.csv. Check that IDF contains" \
                                                                                   "fuel factors for electricity and natural" \
                                                                                   "gas."
        emissions.to_csv(os.path.join(self.resources_dir, 'emissions.csv'), index=False)

    def generate_prices(self):
        prices = pd.DataFrame(index=self.datetime_index)
        prices['month'] = self.datetime_index.month
        electedtariffs = self.summary.get_table_df('Economics Results Summary Report_Entire Facility', 'Tariff Summary')

        for tariff in self.epm.UtilityCost_Tariff:

            if electedtariffs.loc[electedtariffs.index == tariff.name.upper()]['Selected'].values[0] == 'Yes':
                if tariff.output_meter_name == 'electricity:facility':
                    name = 'PriceElectricPower'
                elif tariff.output_meter_name == 'naturalgas:facility':
                    name = 'PriceGasPower'
                else:
                    name = tariff.output_meter_name

                charges = tariff.get_pointing_records()
                simplecharge = 0
                tax = 0
                for query in charges:
                    for charge in getattr(charges, query):
                        # todo: find IDF with block charge and adapt this part
                        # if hasattr(query, 'utility_cost_charge_block_name') and name == 'PriceElectricPower':
                        #     # BOPTEST KPIs do not take energy blocks into account, so we average them here.
                        #     # we also prepare a tariff based on blocks for future usage.
                        #     # todo add dynamic and highly dynamic pricing
                        #     costBlocks = {}
                        #     for block in range(1, 16):
                        #         attr = getattr(charge, 'block_' + block + '_cost_per_unit_value_or_variable_name')
                        #         if attr is float:
                        #             costBlocks[getattr(charge, 'block_size_' + block + '_value_or_variable_name')] = attr
                        #     prices[name + 'Constant'] = np.mean([costBlocks[key] for key in costBlocks.keys()])
                        if hasattr(charge, 'utility_cost_charge_simple_name'):
                            if charge.category_variable_name == 'energycharges' and charge.source_variable == 'totalenergy':
                                try:
                                    simplecharge += float(charge.cost_per_unit_value_or_variable_name)
                                except:
                                    if self.debug:
                                        print("Debug: Found variable cost.")
                                    pass
                            elif charge.category_variable_name == 'taxes':
                                try:
                                    tax += float(charge.cost_per_unit_value_or_variable_name)
                                except:
                                    if self.debug:
                                        print("Warning: cannot convert charge value for {} with value {}".format(charge.name, charge.cost_per_unit_value_or_variable_name))
                                    pass
                        elif hasattr(charge, 'january_value'):
                            monthlycosts = {'1': charge.january_value,
                                            '2': charge.february_value,
                                            '3': charge.march_value,
                                            '4': charge.april_value,
                                            '5': charge.may_value,
                                            '6': charge.june_value,
                                            '7': charge.july_value,
                                            '8': charge.august_value,
                                            '9': charge.september_value,
                                            '10': charge.october_value,
                                            '11': charge.november_value,
                                            '12': charge.december_value}
                            if 'Gas' in name:
                                prices[name] = prices.apply(lambda row: monthlycosts[str(row['month'])], axis=1)
                            if 'Electric' in name:
                                prices[name + 'Constant'] = prices.apply(lambda row: monthlycosts[str(row['month'])],
                                                                         axis=1)
                                prices[name + 'Dynamic'] = prices[name + 'Constant']
                                prices[name + 'HighlyDynamic'] = prices[name + 'Constant']

                if simplecharge > 0:
                    simpleprice = round(simplecharge * (1 + tax), 4)
                    if 'Electric' in name:
                        prices[name + 'Constant'] = simpleprice
                        prices[name + 'Dynamic'] = prices[name + 'Constant']
                        prices[name + 'HighlyDynamic'] = prices[name + 'Constant']
                    if 'Gas' in name:
                        prices[name] = simpleprice
                elif tax > 0:
                    if 'Gas' in name:
                        prices[name] = prices[name].apply(applyTax, args=[tax])
        prices.drop(columns=['month'], inplace=True)
        prices['time'] = self.time
        prices.to_csv(os.path.join(self.resources_dir, 'prices.csv'), index=False)

    def getZones(self):
        self.zones = []
        for zone in self.epm.zone:
            if zone.part_of_total_floor_area == 'yes':
                self.zones.append(zone.name.lower())

    def get_summary(self, table, item, zone):
        keys = self.summary.get_report_keys()
        if table in keys:
            summarylist = self.summary.get_table_report_list(table)
            if item in summarylist:
                summary = self.summary.get_table_df(table, item)
        return summary[(summary.index == zone.upper())]

    def generateOccupancy(self):
        occupancy = {}
        radiantFractionPpl = {}
        sensibleFractionPpl = {}
        latentFractionPpl = {}
        totPplGains = {}
        occdataframe = pd.DataFrame()

        # Look for people instance
        for people in self.epm.people:
            if people.zone_or_zonelist_name.name in self.zones:
                # get occupancy fraction
                occupancy[people.zone_or_zonelist_name.name] = self.fromEPSchedToList(self.epm.Schedule_Compact.one(lambda x: x.name == people.number_of_people_schedule_name.name))#(self.epm.Schedule_Compact[people.number_of_people_schedule_name])
                totPplGains[people.zone_or_zonelist_name.name] = self.fromEPSchedToList(
                    self.epm.Schedule_Compact.one(lambda x: x.name == people.activity_level_schedule_name.name))
                # todo: add sensible/latent split here. Need to simulate the model and look at the outputs
                zonesummary = self.get_summary('Input Verification and Results Summary_Entire Facility', 'Zone Summary', people.zone_or_zonelist_name.name.upper())
                zonearea = zonesummary['Area [m2]'].values[0]
                if people.number_of_people_calculation_method == 'area/person':
                    areaperperson = people.zone_floor_area_per_person
                else:
                    raise NotImplementedError("People calucation method not implemented yet: {}".format(people.number_of_people_calculation_method))
                nompeople = zonearea/areaperperson
                occupancy[people.zone_or_zonelist_name.name] = [item * nompeople for item in occupancy[people.zone_or_zonelist_name.name]]
                totPplGains[people.zone_or_zonelist_name.name] = [a*b for a,b in zip(totPplGains[people.zone_or_zonelist_name.name],occupancy[people.zone_or_zonelist_name.name])]
                radiantFractionPpl[people.zone_or_zonelist_name.name] = [people.fraction_radiant * item for item in totPplGains[people.zone_or_zonelist_name.name]]
                if people.sensible_heat_fraction == 'autocalculate':
                    if self.debug == True:
                        print('Debug: Assuming sensible fraction for heat gains from people to be 0.55')
                    sensibleFraction = 0.55
                else:
                    sensibleFraction = people.sensible_heat_fraction
                sensibleFractionPpl[people.zone_or_zonelist_name.name] = [sensibleFraction * (1 - people.fraction_radiant) * item
                                                                          for item in totPplGains[people.zone_or_zonelist_name.name]]
                latentFractionPpl[people.zone_or_zonelist_name.name] = [
                    (1 - sensibleFraction) * (1 - people.fraction_radiant) * item
                    for item in totPplGains[people.zone_or_zonelist_name.name]]
                occdataframe['Occupancy[{}]'.format(people.zone_or_zonelist_name.name)] = occupancy[people.zone_or_zonelist_name.name]
                occdataframe['PeopleInternalGainsCon[{}]'.format(people.zone_or_zonelist_name.name)] = sensibleFractionPpl[people.zone_or_zonelist_name.name]
                occdataframe['PeopleInternalGainsRad[{}]'.format(people.zone_or_zonelist_name.name)] = \
                radiantFractionPpl[people.zone_or_zonelist_name.name]
                occdataframe['PeopleInternalGainsLat[{}]'.format(people.zone_or_zonelist_name.name)] = \
                latentFractionPpl[people.zone_or_zonelist_name.name]
                occdataframe['UpperCO2[{}]'.format(people.zone_or_zonelist_name.name)] = \
                    np.where(occdataframe['Occupancy[{}]'.format(people.zone_or_zonelist_name.name)] > 0, 800, 1500) #800ppm for offices, ASHRAE Standard 62
                #todo: find a way to extract the CO2 levels from some IDFs if available.

        while len(occdataframe) <= len(self.datetime_index):
            occdataframe = occdataframe.append(occdataframe.iloc[:168], ignore_index=True)
        occdataframe = occdataframe.iloc[:len(self.datetime_index)]
        occdataframe.index = self.datetime_index
        return occdataframe

    def generateGains(self):
        equipmentSenGains = {}
        equipmentRadGains = {}
        equipmentLatGains = {}
        lightsSenGains = {}
        lightsRadGains = {}
        gainsDataframe = pd.DataFrame()

        # Look for people instance
        for light in self.epm.lights:
            if light.zone_or_zonelist_name.name in self.zones:
                # get occupancy fraction
                lightsRadGains[light.zone_or_zonelist_name.name] = self.fromEPSchedToList(self.epm.Schedule_Compact.one(lambda x: x.name == light.schedule_name.name))
                lightsSenGains = lightsRadGains
                zonesummary = self.get_summary('Input Verification and Results Summary_Entire Facility', 'Zone Summary', light.zone_or_zonelist_name.name.upper())
                zonearea = zonesummary['Area [m2]'].values[0]

                if light.design_level_calculation_method == 'watts/area':
                    wattperarea = light.watts_per_zone_floor_area
                else:
                    raise NotImplementedError("Light gains calucation method not implemented yet: {}".format(light.design_level_calculation_method))
                nomgain = zonearea * wattperarea
                radfrac = light.fraction_radiant
                gainsDataframe['LightsInternalGainsCon[{}]'.format(light.zone_or_zonelist_name.name)] = \
                    [(1 - radfrac) * item * nomgain for item in
                     lightsSenGains[light.zone_or_zonelist_name.name]]
                gainsDataframe['LightsInternalGainsRad[{}]'.format(light.zone_or_zonelist_name.name)] = \
                    [(radfrac * item * nomgain) for item in lightsRadGains[light.zone_or_zonelist_name.name]]


        for equipment in self.epm.electricequipment:
            if equipment.zone_or_zonelist_name.name in self.zones:
                # get occupancy fraction
                equipmentSenGains[equipment.zone_or_zonelist_name.name] = self.fromEPSchedToList(self.epm.Schedule_Compact.one(lambda x: x.name == equipment.schedule_name.name))
                equipmentRadGains = equipmentSenGains
                equipmentLatGains = equipmentSenGains
                zonesummary = self.get_summary('Input Verification and Results Summary_Entire Facility', 'Zone Summary', equipment.zone_or_zonelist_name.name.upper())
                zonearea = zonesummary['Area [m2]'].values[0]
                if equipment.design_level_calculation_method == 'watts/area':
                    wattperarea = equipment.watts_per_zone_floor_area
                    nomgain = zonearea * wattperarea
                elif equipment.design_level_calculation_method == 'equipmentlevel':
                    nomgain = float(equipment.design_level)
                else:
                    raise NotImplementedError("Internal gains calucation method not implemented yet: {} in {}".format(equipment.design_level_calculation_method, equipment))

                radfrac = equipment.fraction_radiant
                latfrac = equipment.fraction_latent

                equipmentSenGains[equipment.zone_or_zonelist_name.name] = [(1 - radfrac - latfrac) * item * nomgain for item in equipmentSenGains[equipment.zone_or_zonelist_name.name]]
                equipmentLatGains[equipment.zone_or_zonelist_name.name] = [latfrac * item * nomgain for
                                                                           item in equipmentLatGains[
                                                                               equipment.zone_or_zonelist_name.name]]
                equipmentRadGains[equipment.zone_or_zonelist_name.name] = [radfrac * item * nomgain for
                                                                           item in equipmentLatGains[
                                                                               equipment.zone_or_zonelist_name.name]]
                gainsDataframe['EquipInternalGainsCon[{}]'.format(equipment.zone_or_zonelist_name.name)] = \
                equipmentSenGains[equipment.zone_or_zonelist_name.name]
                gainsDataframe['EquipInternalGainsRad[{}]'.format(equipment.zone_or_zonelist_name.name)] = \
                    equipmentRadGains[equipment.zone_or_zonelist_name.name]
                gainsDataframe['EquipInternalGainsLat[{}]'.format(equipment.zone_or_zonelist_name.name)] = \
                    equipmentLatGains[equipment.zone_or_zonelist_name.name]
        while len(gainsDataframe) <= len(self.datetime_index):
            gainsDataframe = gainsDataframe.append(gainsDataframe.iloc[:168], ignore_index=True)
        gainsDataframe = gainsDataframe.iloc[:len(self.datetime_index)]
        gainsDataframe.index = self.datetime_index
        return gainsDataframe


    def fromEPSchedToList(self, schedule):
        fields = []
        for field in schedule:
            if field != schedule.name and field != schedule.schedule_type_limits_name.name and field is not None:
                fields.append(field)
        # find the day types

        weekdays = []
        saturdays = []
        otherdays = []
        alldays = []
        buffer = []
        convert = []
        ind = 0
        for field in fields:
            if ('for' in field or ind == len(fields)-1) and len(buffer)>1:
                # if the buffer is not empty, we are switching to a different day type
                # or we could be looking at the last element of the list
                if ind == len(fields)-1:
                    buffer.append(field)

                if buffer != []:
                    current = self.period
                    # we convert the list from EP format ('Until: hour:minute,value') to a list indexed on the
                    # dataset period defined in the init method.

                    for item in buffer[1:]:

                        if 'until' in item:
                            item = item.replace('until: ', '')
                            item = item.replace(':', '')
                            hod = int(item[:2]) * 3600
                            mod = int(item[3:4]) * 60
                        else:
                            val = float(item)
                            for i in range(current, int(hod + mod + self.period), self.period):
                                convert.append(val)
                            current = int(hod + mod + self.period)
                    # we append the converted buffer to the correct day type
                    if 'weekdays' in buffer[0]:
                        weekdays = convert
                        convert = []
                    elif 'saturday' in buffer[0]:
                        saturdays = convert
                        convert = []
                    elif 'allotherdays' in buffer[0]:
                        otherdays = convert
                        convert = []
                    elif 'alldays' in buffer[0]:
                        alldays = convert
                        convert = []
                    else:
                        convert=[]
                    buffer = []

                #else, we are not through a day type yet so we append the current field value
            if not 'through' in field and isinstance(field, str):
                buffer.append(field)
            ind += 1

        if alldays != []:
            # if the schedule defines all days, we quit the function now
            return alldays * 7

        # we pre-populate a week worth of data with None
        buffer = [None for i in range(0, 7 * 24 * 3600 + self.period, self.period)]
        if weekdays != []:
            # if weekdays are defined, we start the week with a Sunday
            buffer[int(24*3600/self.period):int(6*24*3600/self.period)] = weekdays * 5
        if saturdays != []:
            buffer[int(6*24*3600/self.period):] = saturdays
        if otherdays != []:
            # if otherdays are defined, we fill the gaps here
            for i in range(len(buffer)):
                if buffer[i] is None:
                    buffer[i:int(i + 24*3600/self.period)] = otherdays

        return buffer

def find_eio_and_summary_table(_dir):
    for file in os.listdir(_dir):
        if file.endswith(".eio"):
            eioPath = os.path.join(_dir, file)
        if file == 'eplustbl.csv':
            tblPath = os.path.join(_dir, file)

    return op.Eio(eioPath), op.SummaryTable(tblPath)

def toKelvin(a):
    return a + 273.15
def toCelsius(a):
    return a - 273.15
def applyTax(a, tax=0):
    return round(a * (1 + tax), 4)