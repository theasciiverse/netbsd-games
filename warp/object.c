/* Header: object.c,v 7.0 86/10/08 15:12:55 lwall Exp */

/* Log:	object.c,v
 * Revision 7.0  86/10/08  15:12:55  lwall
 * Split into separate files.  Added amoebas and pirates.
 *
 */

#include "EXTERN.h"
#include "warp.h"
#include "INTERN.h"
#include "object.h"

void
object_init(void)
{
    ;
}

/* Asciiverse: every caller passes y before x, as in the original; the
 * parameters were named the other way round, so objects were placed
 * transposed, past the end of occupant[][] */
OBJECT *
make_object(char typ, char img, int py, int px, int vy, int vx, long energ,
    long mas, OBJECT *where)
{
    OBJECT *obj;

    if (free_root.next == &free_root)
#ifndef lint
	obj = (OBJECT *) malloc(sizeof root);
#else
	obj = Null(OBJECT*);
#endif
    else {
	obj = free_root.next;
	free_root.next = obj->next;
	obj->next->prev = &free_root;
    }
    obj->type = typ;
    obj->image = img;
    obj->next = where;
    obj->prev = where->prev;
    where->prev = obj;
    obj->prev->next = obj;
    obj->velx = vx;
    obj->vely = vy;
    obj->contend = 0;
    obj->strategy = 0;
    obj->flags = 0;
    obj->posx = px;
    obj->posy = py;
    if (typ != Torp && typ != Web) {
	occupant[py][px] = obj;
    }
    obj->energy = energ;
    obj->mass = mas;
    return(obj);
}

void
unmake_object(OBJECT *curobj)
{
    curobj->prev->next = curobj->next;
    curobj->next->prev = curobj->prev;
    if (curobj == movers) {
	movers = curobj->next;
    }
    free_object(curobj);
}

void
free_object(OBJECT *curobj)
{
    curobj->next = free_root.next;
    curobj->prev = &free_root;
    free_root.next->prev = curobj;
    free_root.next = curobj;
}
