schedule = dict(start_day = 'sunday',
                occupied = dict(weekday = [6.0, 22.0],
                                saturday = [6.0, 18.0],
                                sunday = None,
                                ),
                tempSetpoints = dict(occupied = [273.15 + 21, 273.15 + 24],
                                 unoccupied = [273.15 + 15.6, 273.15 + 26.7]),
                co2Setpoints = dict(occupied = 800,
                                    unoccupied = 1000),
                oasetpoints = dict(occupied = [0.08, 0.11],
                                   unoccupied = [0.0, 0.0])
                )

zones = ['core', 'perimeter1', 'perimeter2', 'perimeter3', 'perimeter4']

sensors = dict(zoneTemps = ['senTemRoom_y',
                            'senTemRoom1_y',
                            'senTemRoom2_y',
                            'senTemRoom3_y',
                            'senTemRoom4_y'],
               ahuPower = ['senPowCor_y',
                           'senPowPer1_y',
                           'senPowPer2_y',
                           'senPowPer3_y',
                           'senPowPer4_y']
               )

controls = dict(supervisory = dict(heating = ['PSZACcontroller_oveHeaStpCor_u',
                                           'PSZACcontroller_oveHeaStpPer1_u',
                                           'PSZACcontroller_oveHeaStpPer2_u',
                                           'PSZACcontroller_oveHeaStpPer3_u',
                                           'PSZACcontroller_oveHeaStpPer4_u'],
                                cooling = ['PSZACcontroller_oveCooStpCor_u',
                                           'PSZACcontroller_oveCooStpPer1_u',
                                           'PSZACcontroller_oveCooStpPer2_u',
                                           'PSZACcontroller_oveCooStpPer3_u',
                                           'PSZACcontroller_oveCooStpPer4_u']
                                ),
                lowlevel = dict(heating = ['PSZACcontroller_oveHeaCor_u',
                                           'PSZACcontroller_oveHeaPer1_u',
                                           'PSZACcontroller_oveHeaPer2_u',
                                           'PSZACcontroller_oveHeaPer3_u',
                                           'PSZACcontroller_oveHeaPer4_u'],
                                cooling = ['PSZACcontroller_oveCooCor_u',
                                           'PSZACcontroller_oveCooPer1_u',
                                           'PSZACcontroller_oveCooPer2_u',
                                           'PSZACcontroller_oveCooPer3_u',
                                           'PSZACcontroller_oveCooPer4_u'],
                                damper = ['PSZACcontroller_oveDamCor_u',
                                          'PSZACcontroller_oveDamP1_u',
                                          'PSZACcontroller_oveDamP2_u',
                                          'PSZACcontroller_oveDamP3_u',
                                          'PSZACcontroller_oveDamP4_u']
                                )
                )

demandlimit = dict(random = False,
                   time = [[14, 16]],
                   maxpow = 10000,
                   )