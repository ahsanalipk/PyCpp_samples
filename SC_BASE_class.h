/*
 * BASE_class.h
 *
 *  Created on: 13.10.2017
 *      Author: ahsanali
 */

#ifndef FI_LIB_BASE_FI_D_H_
#define FI_LIB_BASE_FI_D_H_

// SC for sources
#include <systemc>
#include <systemc-ams>

// Test bench utilities and sources
#include <sca_basic_libraries/generic_tb_utilities/tb_utilities.h>
#include <sca_basic_libraries/generic_tb_utilities/object_access_utils.h>
#include <sca_basic_libraries/arithmetic_sc/mux2c_sc.h>
#include <sca_basic_libraries/arithmetic_sc/add2_sc.h>

template <typename U>
struct struct_sc_d_ports{
	sc_core::sc_in<U>*  fi_n_sc_in   = NULL;
	sc_core::sc_out<U>* fi_n_sc_out  = NULL;
	sca_tdf::sc_in<U>*  fi_n_tdf_in  = NULL;
	sca_tdf::sc_out<U>* fi_n_tdf_out = NULL;

	struct_sc_d_ports( sc_core::sc_in<U>*  fi_node_) : fi_n_sc_in(   fi_node_) {}
	struct_sc_d_ports( sc_core::sc_out<U>* fi_node_) : fi_n_sc_out(  fi_node_) {}
	struct_sc_d_ports( sca_tdf::sc_in<U>*  fi_node_) : fi_n_tdf_in(  fi_node_) {}
	struct_sc_d_ports( sca_tdf::sc_out<U>* fi_node_) : fi_n_tdf_out( fi_node_) {}
};


// Base class template for FI Digital  //sc_port<sc_signal_inout_if<T> >
template <class T>
class BASE_class {
public:

	sc_core::sc_signal<T>* sig_main_fi;		// Main FI Signal from Derived Class
    sc_core::sc_signal<T>* sig_mux_ok;		// Bound to old signal and Mux_in_0
    sc_core::sc_signal<T>* sig_mux_fi;		// Bound to faulty signal and Mux_in_1
    sc_core::sc_signal<T>* sig_mux_out;		// Bound to target port and Mux_out
	sc_core::sc_signal<bool>* sig_mux_sel;	// Displays Mux Selection

	mux2c_sc<T>* mux_insert;			// To choose between old and faulty signal during runtime
	add2_sc<T>* adder_insert;			// To choose SET or ADD FI


	BASE_class(struct_sc_d_ports<T> fi_node, bool add_to_ok){

		// Initialize signals and get old port / channel
		sig_main_fi = new sc_core::sc_signal<T>;
		sig_mux_fi  = new sc_core::sc_signal<T>;
		sig_mux_ok  = new sc_core::sc_signal<T>;
		sig_mux_out = new sc_core::sc_signal<T>;
		sig_mux_sel = new sc_core::sc_signal<bool>;


		// Reconnecting FI based on the target port
		std::string fi_n_kind = "NONE!";

		if (fi_node.fi_n_sc_in != NULL){
			sc_interface* old_ch = fi_node.fi_n_sc_in->get_interface();
			fi_n_kind = std::string( fi_node.fi_n_sc_in->kind() );
			sig_mux_ok = dynamic_cast <sc_core::sc_signal<T>*> (old_ch);
			SC_RECONNECT_PORT ( *fi_node.fi_n_sc_in, *sig_mux_out);
		}
		else if (fi_node.fi_n_sc_out != NULL){
			sc_interface* old_ch = fi_node.fi_n_sc_out->get_interface();
			fi_n_kind = std::string( fi_node.fi_n_sc_out->kind() );
			sig_mux_out = dynamic_cast <sc_core::sc_signal<T>*> (old_ch);
			SC_RECONNECT_PORT ( *fi_node.fi_n_sc_out, *sig_mux_ok);
		}
		else if (fi_node.fi_n_tdf_in != NULL){
			sc_interface* old_ch = fi_node.fi_n_tdf_in->get_interface();
			fi_n_kind = std::string( fi_node.fi_n_tdf_in->kind() );
			sig_mux_ok = dynamic_cast <sc_core::sc_signal<T>*> (old_ch);
			SC_RECONNECT_PORT ( *fi_node.fi_n_tdf_in, *sig_mux_out);
		}
		else if (fi_node.fi_n_tdf_out != NULL){
			sc_interface* old_ch = fi_node.fi_n_tdf_out->get_interface();
			fi_n_kind = std::string( fi_node.fi_n_tdf_out->kind() );
			sig_mux_out = dynamic_cast <sc_core::sc_signal<T>*> (old_ch);
			SC_RECONNECT_PORT ( *fi_node.fi_n_tdf_out, *sig_mux_ok);
		}
		else{
			std::cout<< "No compatible target port specified!\nNO FAULT INJECTION!\n";
		}
		std::cout<< "\nPort kind re-connected: " << fi_n_kind<< std::endl;


		// Select if FI is additional to old signal or totally new
		if (add_to_ok == true){
			adder_insert = new add2_sc<T> ("adder_insert");
			adder_insert-> sc0_i (*sig_mux_ok);
			adder_insert-> sc1_i (*sig_main_fi);
			adder_insert-> sc_o (*sig_mux_fi);
		}
		else{
			adder_insert = NULL;
			sig_mux_fi = sig_main_fi;
		}


	    // Multiplex the original and FI signals
		mux_insert = new mux2c_sc<T> ("mux_insert");
		mux_insert-> sc0_i (*sig_mux_ok);
		mux_insert-> sc1_i (*sig_mux_fi);
		mux_insert-> sc_o  (*sig_mux_out);
	}

	// FI Enable Disable method
	void fi_enable (bool en){
		mux_insert->p.ctrl = en;
		sig_mux_sel->write(en);
	}

	virtual ~BASE_class(){}
};

#endif /* FI_LIB_BASE_FI_D_H_ */
