from gluon import *

PART_OF_URI = 'http://purl.obolibrary.org/obo/BFO_0000050'

def update_participants(db):
    '''this will eventually fix a problem where the structure of individual 
    participants is not 
    captured in element chains when used secondarily in subsequent participants'''
    ptc_table = build_participant_chains(db)
    ptc_keys = ptc_table.keys()  # grab once, so order of traveral is consistent
    for ptc in ptc_keys:
        print("participant: {0}".format(ptc.id))
        chain = ptc_table[ptc]
        update_one_participant_aux(db, ptc, chain, ptc_table, ptc_keys)

def update_one_participant(db, ptc_id):
    ptc_table = build_participant_chains(db)
    ptc_keys = ptc_table.keys()
    print("ptc_keys = {0}".format(repr(ptc_keys)))
    ptc = db.participant(ptc_id)
    chain = build_one_participant_chain(db, ptc)
    update_one_participant_aux(db, ptc, chain, ptc_table, ptc_keys)

def update_one_participant_aux(db, ptc, chain, ptc_table, ptc_keys):
    for ele_spec1 in chain:
        if ele_spec1[0] == 'Individual':
            ele_score = len(chain) - chain.index(ele_spec1)
            best = best_element_match(ptc, ptc_table, ptc_keys, ele_spec1)
            if best[0] > ele_score:
                print("Element needs updating; score = {0}, chain = {1}".format(ele_score, chain))
                msg_str = "Best Match len = {0}\n\t ele2 = {1}\n\t chain = {2}"
                print(msg_str.format(best[0],
                                     best[1],
                                     best[2]))
                print get_plink_n(db, ptc, chain.index(ele_spec1))
                fix_element_chain(db, ptc, ele_spec1, chain, best)


def fix_element_chain(db, ptc, element_spec, chain, best):
    ''' actually extends the element chain '''
    indiv_code = get_participant_code(db, 'individual')
    part_of_property = get_property(db,PART_OF_URI)
    best_score, ptc2_id, best_chain = best
    chain_index = len(best_chain) - best_score + 1
    new_template = best_chain[chain_index:]
    start = get_plink_n(db, ptc, chain.index(element_spec))
    if start is None: # start is head element
        print("chain_index = {0}, new_template = {1}".format(chain_index, new_template))
        clink = new_template[0]
        clink_type = clink[0]
        assert clink_type == 'Individual'
        ind_id = clink[1]
        ele_id = insert_participant_element(db, ptc.id, indiv_code)
        insert_element2indiv_map(db, ele_id, ind_id)
        insert_participant_link(db, ptc.head_element,ele_id,part_of_property)
        head_ele = db.participant_link(ptc.head_element)
    else:   # start is in a chain already
        pass
    return None


def best_element_match(ptc, ptc_table, ptc_keys, ele_spec1):
    best_part = None
    longest_match = 0
    for ptc2 in ptc_keys:
        chain2 = ptc_table[ptc2]
        if ele_spec1 in chain2:
            len2 = len(chain2) - chain2.index(ele_spec1)
            if len2 > longest_match:
                longest_match = len2
                best_part = (longest_match, ptc2.id, chain2)
    if best_part:
        return best_part
    else:
        return None

def get_plink_n(db, ptc, n):
    print "n = {0}".format(n)
    cur_ele = ptc.head_element
    count = 0
    print cur_ele
    plink_rows = db(db.participant_link.parent == cur_ele).select()
    if plink_rows:
        plink = plink_rows[0]
        while (count < n) and plink_rows:
            if len(plink_rows) > 1:
                raise RuntimeError("Bad plink")
            cur_ele = plink.child
            plink_rows = db(db.participant_link.parent == cur_ele).select()
            count += 1
        return plink
    else:
        return None


def build_participant_chains(db):
    ptc_table = {}
    for ptc in all_participants(db):
        chain = build_one_participant_chain(db, ptc)
        ptc_table[ptc] = chain
    return ptc_table


def build_one_participant_chain(db, ptc):
    chain = []
    head = ptc.head_element
    cur_ele = head
    plink_rows = db(db.participant_link.parent == cur_ele).select()
    while (plink_rows):
        if len(plink_rows) > 1:
            raise RuntimeError("Bad plink")
        chain = extend_pelement_chain(db, cur_ele, chain)
        plink = plink_rows[0]
        cur_ele = plink.child
        plink_rows = db(db.participant_link.parent == cur_ele).select()
    chain = extend_pelement_chain(db, cur_ele, chain)
    return chain


def extend_pelement_chain(db, cur_ele, chain):
    eleTerm = db(db.pelement2term.element == cur_ele).select()
    eleIndiv = db(db.pelement2individual.element == cur_ele).select()
    if eleTerm:
        chain_link = ("Term", eleTerm[0].term)
        chain.append(chain_link)
    elif eleIndiv:
        chain_link = ("Individual", eleIndiv[0].individual)
        chain.append(chain_link)
    else:
        print "bad element"
    return chain


def all_participants(db):
    return db(db.participant.id >0).select()

def get_participant_code(db, type_str):
    return db(db.participant_type.label == type_str).select().first().id

def get_property(db, uri):
    return db(db.property.source_id == uri).select().first().id

def insert_participant_element(db, participant_id, type_id):
    return db.participant_element.insert(participant=participant_id,
                                         type=type_id)

def insert_element2indiv_map(db, ele_id, indiv_id):
    db.pelement2individual.insert(element=ele_id, individual=indiv_id)


def insert_participant_link(db, parent_id, child_id, property_id):
    db.participant_link.insert(parent=parent_id,
                               child=child_id,
                               property=property_id)
