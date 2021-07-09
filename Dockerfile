FROM michaelwetter/ubuntu-1804_jmodelica_trunk

ARG testcase

USER root

RUN apt-get update && \
    apt-get install -y git && \
    apt-get install -y git-lfs && \
    apt-get install -y sudo

USER developer

ENV ROOT_DIR /usr/local

WORKDIR $HOME

RUN mkdir $HOME/MODELICAPATH && mkdir git && \
    cd git && \
    git lfs install && \
    git clone https://github.com/ibpsa/modelica-ibpsa.git && \
    git clone https://github.com/open-ideas/IDEAS.git && \
    git clone https://github.com/kbenne/modelica-buildings.git && \
    cd modelica-buildings && git checkout issue2054_self_contained_spawn &&  cd .. && \
    ln -s $HOME/git/IDEAS/IDEAS $HOME/MODELICAPATH/IDEAS && \
    ln -s $HOME/git/modelica-buildings/Buildings $HOME/MODELICAPATH/Buildings && \
    ln -s $HOME/git/modelica-ibpsa/IBPSA $HOME/MODELICAPATH/IBPSA && \
    ln -s $ROOT_DIR/JModelica/ThirdParty/MSL/Modelica $HOME/MODELICAPATH/Modelica && \
    ln -s $ROOT_DIR/JModelica/ThirdParty/MSL/ModelicaServices $HOME/MODELICAPATH/ModelicaServices
ENV MODELICAPATH $HOME/MODELICAPATH

ENV ROOT_DIR /usr/local
ENV JMODELICA_HOME $ROOT_DIR/JModelica
ENV IPOPT_HOME $ROOT_DIR/Ipopt-3.12.4
ENV SUNDIALS_HOME $JMODELICA_HOME/ThirdParty/Sundials
ENV SEPARATE_PROCESS_JVM /usr/lib/jvm/java-8-openjdk-amd64/
ENV JAVA_HOME /usr/lib/jvm/java-8-openjdk-amd64/
ENV PYTHONPATH $PYTHONPATH:$JMODELICA_HOME/Python:$JMODELICA_HOME/Python/pymodelica

USER developer

WORKDIR $HOME

# Copy the weather files over to the previous location since upgrading to MBL 8.0.0
RUN mkdir /home/developer/MODELICAPATH/Buildings/Resources/Data/ThermalZones/EnergyPlus/Examples
RUN cp -r /home/developer/MODELICAPATH/Buildings/Resources/Data/ThermalZones/EnergyPlus/Validation/* /home/developer/MODELICAPATH/Buildings/Resources/Data/ThermalZones/EnergyPlus/Examples

RUN pip install --user flask-restful pandas

RUN mkdir models && \
    mkdir doc

COPY testcases/${testcase}/models/*.fmu models/
COPY testcases/${testcase}/doc/ doc/
COPY testcases/${testcase}/config.py ./
COPY restapi.py ./
COPY testcase.py ./

COPY data data/
COPY forecast forecast/
COPY kpis kpis/
ENV PYTHONPATH $PYTHONPATH:$HOME
