/*
 * ADD_SIGNAL.h
 *
 *  Created on: 25.10.2017
 *      Author: ahsanali
 */

#ifndef LIB_ADD_SIGNAL_H_
#define LIB_ADD_SIGNAL_H_

#include "BASE_class.h"


template <class T>
class ADD_SIGNAL: public BASE_class<T> {
public:

	ADD_SIGNAL(sc_core::sc_module_name nm, struct_sc_a_ports<T> fi_node, sca_tdf::sca_signal<T>* fi_in)
	: BASE_class<T> (fi_node, true){

		SC_RECONNECT_PORT ( this->adder_insert->tdf1_i, *fi_in);
		this->sig_main_fi = fi_in;
	}

	ADD_SIGNAL(sc_core::sc_module_name nm, struct_sc_a_ports<T> fi_node, sca_tdf::sca_out<T>* fi_in)
	: BASE_class<T> (fi_node, true){

		fi_in->bind(*this->sig_main_fi);
	}

	virtual ~ADD_SIGNAL(){}
};

#endif /* LIB_ADD_SIGNAL_H_ */
