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
    #git clone https://github.com/ibpsa/modelica-ibpsa.git && \
    #git clone https://github.com/open-ideas/IDEAS.git && \
    git clone https://github.com/lbl-srg/modelica-buildings.git && \
    git clone https://github.com/henze-research-group/modrlc-models.git && \
    cd modrlc-models && git checkout actb-resources && cd .. && \
    #ln -s $HOME/git/IDEAS/IDEAS $HOME/MODELICAPATH/IDEAS && \
    ln -s $HOME/git/modelica-buildings/Buildings $HOME/MODELICAPATH/Buildings && \
    #ln -s $HOME/git/modelica-ibpsa/IBPSA $HOME/MODELICAPATH/IBPSA && \
    ln -s $ROOT_DIR/JModelica/ThirdParty/MSL/Modelica $HOME/MODELICAPATH/Modelica && \
    ln -s $ROOT_DIR/JModelica/ThirdParty/MSL/ModelicaServices $HOME/MODELICAPATH/ModelicaServices && \

    # Temporary fix. Instead, update Spawn binaries in next revision.
    cd modelica-buildings/Buildings/Resources/bin/spawn-linux64/bin && mv spawn-0.2.0-d7f1e095f3 spawn
ENV MODELICAPATH $HOME/MODELICAPATH

ENV ROOT_DIR /usr/local
ENV JMODELICA_HOME $ROOT_DIR/JModelica
ENV IPOPT_HOME $ROOT_DIR/Ipopt-3.12.4
ENV SUNDIALS_HOME $JMODELICA_HOME/ThirdParty/Sundials
ENV SEPARATE_PROCESS_JVM /usr/lib/jvm/java-8-openjdk-amd64/
ENV JAVA_HOME /usr/lib/jvm/java-8-openjdk-amd64/
ENV PYTHONPATH $PYTHONPATH:$JMODELICA_HOME/Python:$JMODELICA_HOME/Python/pymodelica

USER root
# Edit pyfmi to event update at start of simulation for ME2
RUN sed -i "350 i \\\n        if isinstance(self.model, fmi.FMUModelME2):\n            self.model.event_update()" $JMODELICA_HOME/Python/pyfmi/fmi_algorithm_drivers.py

USER developer

WORKDIR $HOME

RUN pip install --user flask-restful==0.3.9 pandas==0.24.2 flask_cors==3.0.10

RUN mkdir models && \
    mkdir doc

COPY testcases/${testcase}/models/*.fmu models/
COPY testcases/${testcase}/doc/ doc/
COPY restapi.py ./
COPY testcase.py ./
COPY version.txt ./

COPY data data/
COPY forecast forecast/
COPY kpis kpis/
ENV PYTHONPATH $PYTHONPATH:$HOME
