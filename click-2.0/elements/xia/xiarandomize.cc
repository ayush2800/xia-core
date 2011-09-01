/*
 * xiarandomize.{cc,hh} -- randomizes an address of an XIA packet
 */

#include <click/config.h>
#include "xiarandomize.hh"
#include <click/glue.hh>
#include <click/error.hh>
#include <click/confparse.hh>
#include <clicknet/xia.h>
#if CLICK_USERLEVEL
#include <stdlib.h>
#endif
CLICK_DECLS

XIARandomize::XIARandomize()
{
    assert(CLICK_XIA_XID_ID_LEN % sizeof(uint32_t) == 0);

#if CLICK_USERLEVEL
    _xsubi_det[0] = 1;
    _xsubi_det[1] = 2;
    _xsubi_det[2] = 3;
#elif CLICK_LINUXMODULE
    _deterministic.s1 = 1;
    _deterministic.s2 = 2;
    _deterministic.s3=  3;
#endif

    _current_cycle = 0;
    _max_cycle = 1000000000;

#if CLICK_USERLEVEL
    _xsubi_arb[0] = 4;
    _xsubi_arb[1] = 5;
    _xsubi_arb[2] = 6;
#elif CLICK_LINUXMODULE
    _arbitrary.s1 = 4;
    _arbitrary.s2 = 5;
    _arbitrary.s3 = 6;
#endif
}

XIARandomize::~XIARandomize()
{
}

int
XIARandomize::configure(Vector<String> &conf, ErrorHandler *errh)
{
    return cp_va_kparse(conf, this, errh,
                        "XID_TYPE", cpkP+cpkM, cpXIDType, &_xid_type,
			"MAX_CYCLE", 0, cpInteger, &_max_cycle,
			cpEnd);
}

Packet *
XIARandomize::simple_action(Packet *p_in)
{
    WritablePacket *p = p_in->uniqueify();
    if (!p)
        return 0;

    click_xia *hdr = p->xia_header();

    for (size_t i = 0; i < hdr->dnode + hdr->snode; i++)
    {
        struct click_xia_xid_node& node = hdr->node[i];
        if (node.xid.type == 1)
        {
            node.xid.type = _xid_type;
            uint8_t* xid = node.xid.id;
            const uint8_t* xid_end = xid + CLICK_XIA_XID_ID_LEN;

            while (xid != xid_end)
            {
#if CLICK_USERLEVEL
                *reinterpret_cast<uint32_t*>(xid) = static_cast<uint32_t>(nrand48(_xsubi_det));
#elif CLICK_LINUXMODULE
                *reinterpret_cast<uint32_t*>(xid) = static_cast<uint32_t>(prandom32(&_deterministic));
#endif
                xid += sizeof(uint32_t);
            }

            if (++_current_cycle == _max_cycle)
	    {
#if CLICK_USERLEVEL
		    _xsubi_det[0] = 1;
		    _xsubi_det[1] = 2;
		    _xsubi_det[2] = 3;
#elif CLICK_LINUXMODULE
		    _deterministic.s1 = 1;
		    _deterministic.s2 = 2;
		    _deterministic.s3 = 3;
#endif
		    _current_cycle = 0;
	    }
        }
        else if (node.xid.type == 2)
        {
            node.xid.type = _xid_type;
            uint8_t* xid = node.xid.id;
            const uint8_t* xid_end = xid + CLICK_XIA_XID_ID_LEN;

            while (xid != xid_end)
            {
#if CLICK_USERLEVEL
                *reinterpret_cast<uint32_t*>(xid) = static_cast<uint32_t>(nrand48(_xsubi_arb));
#elif CLICK_LINUXMODULE
                *reinterpret_cast<uint32_t*>(xid) = static_cast<uint32_t>(prandom32(&_arbitrary));
#endif
                xid += sizeof(uint32_t);
            }
        }
    }

    return p;
}

CLICK_ENDDECLS
EXPORT_ELEMENT(XIARandomize)
ELEMENT_MT_SAFE(XIARandomize)
